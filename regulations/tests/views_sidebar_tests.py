import re
from unittest import TestCase

from mock import patch
from django.test.client import Client

from regulations.generator import node_types


class ViewsSideBarViewTest(TestCase):
    """Integration tests for the sidebar"""

    @patch('regulations.views.sidebar.api_reader')
    def test_get(self, api_reader):
        api_reader.ApiReader.return_value.layer.return_value = {
            '876-12': [
                {'reference': ['1992-1', '876-12']},
                {'reference': ['1992-2', '876-12']},
            ],
            '876-12-a': [{'reference': ['1992-1', '876-12-a']}]
        }
        api_reader.ApiReader.return_value.regulation.return_value = {
            'label': ['876', '12'],
            'node_type': node_types.REGTEXT,
            'children': [
                {'label': ['876', '12', 'a'], 'children': [],
                 'node_type': node_types.REGTEXT},
                {'label': ['876', '12', 'b'], 'children': [],
                 'node_type': node_types.REGTEXT},
                {'label': ['876', '12', 'c'], 'node_type': node_types.REGTEXT,
                 'children': [
                     {'label': ['876', '12', 'c', '1'], 'children': [],
                      'node_type': node_types.REGTEXT}]}
            ]
        }
        response = Client().get('/partial/sidebar/1111-7/verver')

        sxs_start = response.content.find(b'<section id="sxs-list"')
        sxs_end = response.content.find(b'</section>', sxs_start)
        sxs = response.content[sxs_start:sxs_end]

        self.assertTrue(bool(re.search(br'\b12\b', sxs)))
        self.assertIn(b'12(a)', sxs)
        self.assertIn(b'1992-2', sxs)
        self.assertIn(b'876-12', sxs)
        self.assertIn(b'1992-1', sxs)
        self.assertIn(b'876-12-a', sxs)
        self.assertNotIn(b'876-12-b', sxs)
