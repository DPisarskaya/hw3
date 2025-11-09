import pytest
import sys
import os

# Добавляем путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import BookScraper

class TestGetBookData:
    """Тесты для метода get_book_data"""
    
    def test_returns_dict_with_required_keys(self):
        """Проверяет, что функция возвращает словарь с нужными ключами"""
        
        # Создаем экземпляр класса
        scraper = BookScraper()
        
        # Используем известную рабочую книгу для тестирования
        test_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
        
        # Вызываем метод класса
        result = scraper.get_book_data(test_url)
        
        # Проверяем, что результат - словарь
        assert isinstance(result, dict)
        
        # Проверяем наличие всех обязательных ключей
        required_keys = [
            'title', 'price', 'rating', 'availability', 'description'
        ]
        
        for key in required_keys:
            assert key in result, f"Ключ '{key}' отсутствует в результате"
    
    def test_book_data_values_correct(self):
        """Проверяет корректность значений полей"""
        scraper = BookScraper()
        test_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
        
        result = scraper.get_book_data(test_url)
        
        # Проверяем конкретные значения
        assert result['title'] == "A Light in the Attic"
        assert result['url'] == test_url

class TestScrapeBooks:
    """Тесты для метода scrape_books"""
    
    def test_returns_list_of_books(self):
        """Проверяет, что функция возвращает список книг"""
        
        scraper = BookScraper()
        
        # Используем тестовую категорию
        test_category_url = "http://books.toscrape.com/catalogue/category/books/travel_2/index.html"
        
        # Вызываем метод с ограничением количества книг
        result = scraper.scrape_books(test_category_url, max_books=3)
        
        # Проверяем структуру результата
        assert isinstance(result, dict)
        assert 'books' in result
        assert 'total_books' in result
        
        # Проверяем, что books - это список
        assert isinstance(result['books'], list)
        assert len(result['books']) > 0
        assert result['total_books'] == len(result['books'])
    
    def test_returns_expected_number_of_books(self):
        """Проверяет, что возвращается ожидаемое количество книг"""
        scraper = BookScraper()
        test_category_url = "http://books.toscrape.com/catalogue/category/books/travel_2/index.html"
        
        # Запрашиваем 2 книги
        result = scraper.scrape_books(test_category_url, max_books=2)
        
        assert result['total_books'] == 2
        assert len(result['books']) == 2
        
        # Проверяем, что каждая книга - словарь с нужными ключами
        for book in result['books']:
            assert isinstance(book, dict)
            assert 'title' in book
            assert 'price' in book

class TestEdgeCases:
    """Тесты для крайних случаев"""
    
    def test_invalid_url_handling(self):
        """Проверяет обработку неверного URL"""
        scraper = BookScraper()
        invalid_url = "http://invalid-url-that-does-not-exist.com"
        
        result = scraper.get_book_data(invalid_url)
        
        # Проверяем, что возвращается словарь с ошибкой
        assert isinstance(result, dict)
        assert 'error' in result
    
    def test_empty_category(self):
        """Проверяет обработку пустой категории"""
        scraper = BookScraper()
        # Используем несуществующую категорию
        invalid_category_url = "http://books.toscrape.com/catalogue/category/books/invalid_category/index.html"
        
        result = scraper.scrape_books(invalid_category_url)
        
        # Проверяем обработку ошибки
        assert isinstance(result, dict)
        assert 'error' in result