from lxml import etree
import re

from indigo.analysis.markup import TextPatternMarker
from indigo.plugins import LocaleBasedMatcher, plugins


class BaseItalsFinder(LocaleBasedMatcher, TextPatternMarker):
    """ Italicises terms in a document.
    """
    marker_tag = 'i'
    candidate_xpath = ".//text()[not(ancestor::a:i)]"

    def mark_up_italics_in_document(self, document, italics_terms):
        """ Find and italicise terms in +document+, which is an Indigo Document object.
        """
        # we need to use etree, not objectify, so we can't use document.doc.root,
        # we have to re-parse it
        root = etree.fromstring(document.content)
        self.setup(root)
        self.get_pattern_re(italics_terms)
        self.markup_patterns(root)
        document.content = etree.tostring(root, encoding='utf-8').decode('utf-8')

    def get_pattern_re(self, italics_terms):
        # TODO: do this differently once italics_terms stored as an actual array
        f_string = f'{italics_terms[0]}'.replace('\r\n', '|').replace(' ', '\s*')
        self.pattern_re = re.compile(rf'(?P<itals>{f_string})', re.X)

    def markup_match(self, node, match):
        """ Markup the match with a <i> tag.
        """
        itals = etree.Element(self.marker_tag)
        itals.text = match.group('itals')
        return itals, match.start('itals'), match.end('itals')


@plugins.register('italics-terms')
class ItalsFinderENG(BaseItalsFinder):
    """ Finds references to italics terms in English documents.
    """
    # country, language, locality
    locale = (None, 'eng', None)
