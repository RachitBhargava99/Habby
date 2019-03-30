import unittest

from backend.tests.BaseCases import BaseTestCase


class FlaskTestCases(BaseTestCase):

    # Ensure that Flask was set up correctly
    def test_index(self):
        response = self.client.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Ensure that the application can search without a zip code and page number
    def test_search(self):
        # 1 Category
        response1 = self.client.post('/search',
                                     json={'cat': ['101']}
                                     )
        # 2 Categories
        response2 = self.client.post('/search',
                                     json={'cat': ['101', '103']}
                                     )
        # 3 Categories
        response3 = self.client.post('/search',
                                     json={'cat': ['101', '102', '103']}
                                     )

        self.assert200(response1)
        self.assert200(response2)
        self.assert200(response3)

    # Ensure that the application can search without a zip code but with a page number
    def test_search_page(self):
        # 1 Category
        response1 = self.client.post('/search',
                                     json={'cat': ['101'],
                                           'page_num': 13}
                                     )
        # 2 Categories
        response2 = self.client.post('/search',
                                     json={'cat': ['101', '103'],
                                           'page_num': 13}
                                     )
        # 3 Categories
        response3 = self.client.post('/search',
                                     json={'cat': ['101', '102', '103'],
                                           'page_num': 13}
                                     )

        self.assert200(response1)
        self.assert200(response2)
        self.assert200(response3)

    # Ensure that the application can search with a zip code but without a page number
    def test_search_zip(self):
        # 1 Category
        response1 = self.client.post('/search',
                                     json={'cat': ['101'],
                                           'zip_code': '30332',
                                           'loc_radius': '25mi'}
                                     )
        # 2 Categories
        response2 = self.client.post('/search',
                                     json={'cat': ['101', '103'],
                                           'zip_code': '30332',
                                           'loc_radius': '25mi'}
                                     )
        # 3 Categories
        response3 = self.client.post('/search',
                                     json={'cat': ['101', '102', '103'],
                                           'zip_code': '30332',
                                           'loc_radius': '25mi'}
                                     )

        self.assert200(response1)
        self.assert200(response2)
        self.assert200(response3)

    # Ensure that the application can search with a zip code and a page number
    def test_search_zip_page(self):
        # 1 Category
        response1 = self.client.post('/search',
                                     json={'cat': ['101'],
                                           'page_number': 13,
                                           'zip_code': '30332',
                                           'loc_radius': '25mi'}
                                     )
        # 2 Categories
        response2 = self.client.post('/search',
                                     json={'cat': ['101', '103'],
                                           'page_number': 13,
                                           'zip_code': '30332',
                                           'loc_radius': '25mi'}
                                     )
        # 3 Categories
        response3 = self.client.post('/search',
                                     json={'cat': ['101', '102', '103'],
                                           'page_number': 13,
                                           'zip_code': '30332',
                                           'loc_radius': '25mi'}
                                     )

        self.assert200(response1)
        self.assert200(response2)
        self.assert200(response3)

    # Ensure that the application provides event details
    def test_event_details(self):
        response = self.client.get('/event/1')

        self.assert200(response=response)

    # Ensure that the application provides a category list
    def test_cat_list(self):
        response = self.client.get('/cat/list')

        self.assert200(response)


if __name__ == '__main__':
    unittest.main()
