import logging
import os.path
from lxml.etree import LxmlError

from django.db.models import Manager
from rest_framework import serializers, renderers
from rest_framework.reverse import reverse
from rest_framework.exceptions import ValidationError
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from cobalt import Act, FrbrUri, AmendmentEvent, RepealEvent
from cobalt.act import datestring

from .models import Document, Attachment
from .importer import Importer

log = logging.getLogger(__name__)


class TagSerializer(TaggitSerializer):
    def _save_tags(self, tag_object, tags):
        for key in tags.keys():
            tag_values = tags.get(key)
            getattr(tag_object, key).set(*tag_values)
        return tag_object


class AmendmentSerializer(serializers.Serializer):
    """ Serializer matching :class:`cobalt.act.AmendmentEvent`
    """

    date = serializers.DateField()
    """ Date that the amendment took place """
    amending_title = serializers.CharField()
    """ Title of amending document """
    amending_uri = serializers.CharField()
    """ FRBR URI of amending document """
    amending_id = serializers.SerializerMethodField()
    """ ID of the amending document, if available """

    def get_amending_id(self, instance):
        if hasattr(instance, 'amending_document') and instance.amending_document is not None:
            return instance.amending_document.id


class RepealSerializer(serializers.Serializer):
    """ Serializer matching :class:`cobalt.act.RepealEvent`
    """

    date = serializers.DateField()
    """ Date that the repeal took place """
    repealing_title = serializers.CharField()
    """ Title of repealing document """
    repealing_uri = serializers.CharField()
    """ FRBR URI of repealing document """
    repealing_id = serializers.SerializerMethodField()
    """ ID of the repealing document, if available """

    def validate_empty_values(self, data):
        # we need to override this because for some reason the default
        # value given by DRF if this field isn't provided is {}, not None,
        # and we need to indicate that that is allowed.
        # see https://github.com/tomchristie/django-rest-framework/pull/2796
        if not data:
            return True, data
        return super(RepealSerializer, self).validate_empty_values(data)

    def get_repealing_id(self, instance):
        if hasattr(instance, 'repealing_document') and instance.repealing_document is not None:
            return instance.repealing_document.id


class AttachmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False, write_only=True)
    filename = serializers.CharField(max_length=255, required=False)
    url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    view_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = (
            'id',
            'url', 'download_url', 'view_url',
            'file',
            'filename',
            'mime_type',
            'size',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at', 'mime_type', 'size')

    def get_url(self, instance):
        if not instance.pk:
            return None
        return reverse('document-attachments-detail', request=self.context['request'], kwargs={
            'document_id': instance.document.pk,
            'pk': instance.pk,
        })

    def get_download_url(self, instance):
        if not instance.pk:
            return None
        return reverse('document-attachments-download', request=self.context['request'], kwargs={
            'document_id': instance.document.pk,
            'pk': instance.pk,
        })

    def get_view_url(self, instance):
        if not instance.pk:
            return None
        return reverse('document-attachments-view', request=self.context['request'], kwargs={
            'document_id': instance.document.pk,
            'pk': instance.pk,
        })

    def create(self, validated_data):
        file = validated_data.get('file', None)
        if not file:
            raise ValidationError({'file': "No file was submitted."})

        args = {}
        args.update(validated_data)
        args['size'] = file.size
        args['mime_type'] = file.content_type
        args['filename'] = args.get('filename', os.path.basename(file.name))
        args['document'] = args.get('document', self.context['document'])

        return super(AttachmentSerializer, self).create(args)

    def update(self, instance, validated_data):
        if 'file' in validated_data:
            raise ValidationError("Value of 'file' cannot be updated. Delete and re-create this attachment.")
        return super(AttachmentSerializer, self).update(instance, validated_data)


class DocumentListSerializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        super(DocumentListSerializer, self).__init__(*args, **kwargs)
        # mark on the child that we're doing many, so it doesn't
        # try to decorate the children for us
        self.context['many'] = True

    def to_representation(self, data):
        iterable = data.all() if isinstance(data, Manager) else data

        # Do some bulk post-processing, this is much more efficient
        # than doing each document one at a time and going to the DB
        # hundreds of times.
        Document.decorate_amendments(iterable)
        Document.decorate_amended_versions(iterable)
        Document.decorate_repeal(iterable)

        return super(DocumentListSerializer, self).to_representation(data)


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    content = serializers.CharField(required=False, write_only=True)
    """ A write-only field for setting the entire XML content of the document. """

    content_url = serializers.SerializerMethodField()
    """ A URL for the entire content of the document. The content isn't included in the
    document description because it could be huge. """

    toc_url = serializers.SerializerMethodField()
    """ A URL for the table of content of the document. The TOC isn't included in the
    document description because it could be huge and requires parsing the XML. """

    published_url = serializers.SerializerMethodField()
    """ Public URL of a published document. """

    attachments_url = serializers.SerializerMethodField()
    """ URL of document attachments. """

    file = serializers.FileField(write_only=True, required=False)
    """ Allow uploading a file to convert and override the content of the document. """

    publication_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    publication_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    publication_date = serializers.DateField(required=False, allow_null=True)

    tags = TagListSerializerField(child=serializers.CharField(), required=False)
    amendments = AmendmentSerializer(many=True, required=False)

    amended_versions = serializers.SerializerMethodField()
    """ List of amended versions of this document """
    repeal = RepealSerializer(required=False, allow_null=True)

    class Meta:
        list_serializer_class = DocumentListSerializer
        model = Document
        fields = (
            # readonly, url is part of the rest framework
            'id', 'url',

            'content', 'content_url', 'file',

            'title', 'draft', 'created_at', 'updated_at',
            # frbr_uri components
            'country', 'locality', 'nature', 'subtype', 'year', 'number', 'frbr_uri',

            'publication_date', 'publication_name', 'publication_number',
            'expression_date', 'commencement_date', 'assent_date',
            'language', 'stub', 'tags', 'amendments', 'amended_versions',
            'repeal',

            'published_url', 'toc_url', 'attachments_url',
        )
        read_only_fields = ('locality', 'nature', 'subtype', 'year', 'number', 'created_at', 'updated_at')

    def get_content_url(self, doc):
        if not doc.pk:
            return None
        return reverse('document-content', request=self.context['request'], kwargs={'pk': doc.pk})

    def get_toc_url(self, doc):
        if not doc.pk:
            return None
        return reverse('document-toc', request=self.context['request'], kwargs={'pk': doc.pk})

    def get_attachments_url(self, doc):
        if not doc.pk:
            return None
        return reverse('document-attachments-list', request=self.context['request'], kwargs={'document_id': doc.pk})

    def get_published_url(self, doc, with_date=False):
        if not doc.pk or doc.draft:
            return None
        else:
            uri = doc.doc.frbr_uri
            if with_date and doc.expression_date:
                uri.expression_date = '@' + datestring(doc.expression_date)
            else:
                uri.expression_date = None

            uri = uri.expression_uri()[1:]

            uri = reverse('published-document-detail', request=self.context['request'],
                          kwargs={'frbr_uri': uri})
            return uri.replace('%40', '@')

    def get_amended_versions(self, doc):
        def describe(doc):
            info = {
                'id': d.id,
                'expression_date': datestring(d.expression_date),
            }
            if not d.draft:
                info['published_url'] = self.get_published_url(d, with_date=True)
            return info

        return [describe(d) for d in doc.amended_versions()]

    def validate(self, data):
        """
        We allow callers to pass in a file upload in the ``file`` attribute,
        and overwrite the content XML with that value if we can.
        """
        upload = data.pop('file', None)
        if upload:
            # we got a file
            try:
                document = Importer().import_from_upload(upload)
            except ValueError as e:
                log.error("Error during import: %s" % e.message, exc_info=e)
                raise ValidationError({'file': e.message or "error during import"})
            data['content'] = document.content
            # add the document as an attachment
            data['source_file'] = upload

        return data

    def validate_content(self, value):
        try:
            Act(value)
        except LxmlError as e:
            raise ValidationError("Invalid XML: %s" % e.message)
        return value

    def validate_frbr_uri(self, value):
        try:
            return FrbrUri.parse(value.lower()).work_uri()
        except ValueError:
            raise ValidationError("Invalid FRBR URI")

    def create(self, validated_data):
        document = Document()
        return self.update(document, validated_data)

    def update(self, document, validated_data):
        content = validated_data.pop('content', None)
        amendments = validated_data.pop('amendments', None)
        tags = validated_data.pop('tags', None)
        repeal = validated_data.pop('repeal', None)
        source_file = validated_data.pop('source_file', None)

        # Document content must always come first so it can be overridden
        # by the other properties.
        if content is not None:
            document.content = content

        document = super(DocumentSerializer, self).update(document, validated_data)

        document.repeal = RepealEvent(**repeal) if repeal else None
        if amendments is not None:
            document.amendments = [AmendmentEvent(**a) for a in amendments]
        if tags is not None:
            document.tags.set(*tags)

        if source_file:
            # add the source file as an attachment
            AttachmentSerializer(context={'document': document}).create({'file': source_file})

        document.save()
        return document

    def update_document(self, instance):
        """ Update document without saving it. """
        amendments = self.validated_data.pop('amendments', None)
        repeal = self.validated_data.pop('repeal', None)

        for attr, value in self.validated_data.items():
            setattr(instance, attr, value)

        instance.repeal = RepealEvent(**repeal) if repeal else None

        if amendments is not None:
            instance.amendments = [AmendmentEvent(**a) for a in amendments]

        instance.copy_attributes()
        return instance

    def to_representation(self, instance):
        if not self.context.get('many', False):
            Document.decorate_amendments([instance])
            Document.decorate_amended_versions([instance])
            Document.decorate_repeal([instance])
        return super(DocumentSerializer, self).to_representation(instance)


class ConvertSerializer(serializers.Serializer):
    """
    Helper to handle input elements for the /convert API
    """

    file = serializers.FileField(write_only=True, required=False)
    content = serializers.CharField(write_only=True, required=False)
    inputformat = serializers.ChoiceField(write_only=True, required=False, choices=['application/json', 'text/plain'])
    outputformat = serializers.ChoiceField(write_only=True, required=True, choices=['application/xml', 'application/json', 'text/html'])
    fragment = serializers.CharField(write_only=True, required=False)
    id_prefix = serializers.CharField(write_only=True, required=False)

    def validate(self, data):
        if data.get('content') and not data.get('inputformat'):
            raise ValidationError({'inputformat': "The inputformat field is required when the content field is used"})

        return data


class AkomaNtosoRenderer(renderers.XMLRenderer):
    def render(self, data, media_type=None, renderer_context=None):
        return data
