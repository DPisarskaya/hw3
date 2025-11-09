#!/usr/bin/env python
# coding: utf-8

# # Домашнее задание 3. Парсинг, Git и тестирование на Python
# 
# **Цели задания:**
# 
# * Освоить базовые подходы к web-scraping с библиотеками `requests` и `BeautisulSoup`: навигация по страницам, извлечение HTML-элементов, парсинг.
# * Научиться автоматизировать задачи с использованием библиотеки `schedule`.
# * Попрактиковаться в использовании Git и оформлении проектов на GitHub.
# * Написать и запустить простые юнит-тесты с использованием `pytest`.
# 
# 
# В этом домашнем задании вы разработаете систему для автоматического сбора данных о книгах с сайта [Books to Scrape](http://books.toscrape.com). Нужно реализовать функции для парсинга всех страниц сайта, извлечения информации о книгах, автоматического ежедневного запуска задачи и сохранения результата.
# 
# Важной частью задания станет оформление проекта: вы создадите репозиторий на GitHub, оформите `README.md`, добавите артефакты (код, данные, отчеты) и напишете базовые тесты на `pytest`.
# 
# 

# In[1]:


# get_ipython().system('pip install -q schedule pytest')
# установка библиотек, если ещё не


# In[2]:


# Библиотеки, которые могут вам понадобиться
# При необходимости расширяйте список
import time
import requests
import schedule
from bs4 import BeautifulSoup


# ## Задание 1. Сбор данных об одной книге (20 баллов)
# 
# В этом задании мы начнем подготовку скрипта для парсинга информации о книгах со страниц каталога сайта [Books to Scrape](https://books.toscrape.com/).
# 
# Для начала реализуйте функцию `get_book_data`, которая будет получать данные о книге с одной страницы (например, с [этой](http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html)). Соберите всю информацию, включая название, цену, рейтинг, количество в наличии, описание и дополнительные характеристики из таблицы Product Information. Результат достаточно вернуть в виде словаря.
# 
# **Не забывайте про соблюдение PEP-8** — помимо качественно написанного кода важно также документировать функции по стандарту:
# * кратко описать, что она делает и для чего нужна;
# * какие входные аргументы принимает, какого они типа и что означают по смыслу;
# * аналогично описать возвращаемые значения.
# 
# *P. S. Состав, количество аргументов функции и тип возвращаемого значения можете менять как вам удобно. То, что написано ниже в шаблоне — лишь пример.*

# In[3]:


def get_book_data(book_url: str) -> dict:
   """
   Получает информацию о книге с указанной страницы сайта Books to Scrape.
   
   Функция получает HTML-страницу книги, извлекает основную информацию 
   (название, цену, рейтинг, наличие, описание) и дополнительные 
   характеристики из таблицы Product Information.
   
   Args:
       book_url (str): URL-адрес страницы книги для парсинга
       
   Returns:
       Dict[str, Optional[str]]: Словарь с данными о книге, где ключи:
           - 'title': Название книги
           - 'price': Цена книги
           - 'rating': Рейтинг книги (количество звезд)
           - 'availability': Информация о наличии на складе
           - 'description': Описание книги
           - 'upc': Universal Product Code
           - 'product_type': Тип продукта
           - 'price_excl_tax': Цена без учета налогов
           - 'price_incl_tax': Цена с учетом налогов
           - 'tax': Сумма налогов
           - 'number_of_reviews': Количество отзывов
   
   Raises:
       requests.RequestException: Если произошла ошибка при запросе к странице
       Exception: Если не удалось распарсить данные со страницы
   """

   # НАЧАЛО ВАШЕГО РЕШЕНИЯ

   try:
       # Отправляем запрос к странице книги
       response = requests.get(book_url)
       # Проверяем статус ответа
       response.raise_for_status()
       
       # Создаем объект BeautifulSoup для парсинга
       soup = BeautifulSoup(response.content, 'html.parser')
       
       # Извлекаем основную информацию о книге
       title = soup.find('h1').text.strip()
       price = soup.find('p', class_='price_color').text.strip()
       
       # Извлекаем рейтинг (преобразуем классы звезд в числовое значение)
       rating_element = soup.find('p', class_='star-rating')
       rating_classes = rating_element.get('class')
       rating_map = {'One': '1', 'Two': '2', 'Three': '3', 'Four': '4', 'Five': '5'}
       rating = None
       for class_name in rating_classes:
           if class_name in rating_map:
               rating = rating_map[class_name]
               break
       
       # Извлекаем информацию о наличии
       availability = soup.find('p', class_='availability').text.strip()
       
       # Извлекаем описание
       description_element = soup.select_one('#product_description + p')
       description = description_element.text.strip() if description_element else None
       
       # Извлекаем данные из таблицы Product Information
       product_info = {}
       info_table = soup.find('table', class_='table table-striped')
       if info_table:
           rows = info_table.find_all('tr')
           for row in rows:
               header = row.find('th').text.strip()
               value = row.find('td').text.strip()
               product_info[header] = value
       
       # Формируем итоговый словарь с данными
       book_data = {
           'title': title,
           'price': price,
           'rating': rating,
           'availability': availability,
           'description': description,
           'upc': product_info.get('UPC'),
           'product_type': product_info.get('Product Type'),
           'price_excl_tax': product_info.get('Price (excl. tax)'),
           'price_incl_tax': product_info.get('Price (incl. tax)'),
           'tax': product_info.get('Tax'),
           'number_of_reviews': product_info.get('Number of reviews')
       }
       
       return book_data
       
   except requests.RequestException as e:
       raise requests.RequestException(f"Ошибка при запросе к {book_url}: {e}")
   except Exception as e:
       raise Exception(f"Ошибка при парсинге данных: {e}") 
       
   # КОНЕЦ ВАШЕГО РЕШЕНИЯ


# In[4]:


# Используйте для самопроверки
book_url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
get_book_data(book_url)


# ## Задание 2. Сбор данных обо всех книгах (20 баллов)
# 
# Создайте функцию `scrape_books`, которая будет проходиться по всем страницам из каталога (вида `http://books.toscrape.com/catalogue/page-{N}.html`) и осуществлять парсинг всех страниц в цикле, используя ранее написанную `get_book_data`.
# 
# Добавьте аргумент-флаг, который будет отвечать за сохранение результата в файл: если он будет равен `True`, то информация сохранится в ту же папку в файл `books_data.txt`; иначе шаг сохранения будет пропущен.
# 
# **Также не забывайте про соблюдение PEP-8**

# In[5]:


def scrape_books(is_save: bool = False) -> dict:
    """
    Получает данные о книгах со всех страниц каталога Books to Scrape.
    
    Функция проходит по всем страницам каталога, извлекает ссылки на книги
    и собирает информацию о каждой книге с помощью функции get_book_data.
    
    Args:
        is_save (bool, optional): Флаг сохранения результатов в файл.
            Если True, данные сохраняются в файл 'books_data.txt'.
            По умолчанию False.
            
    Returns:
        List[Dict[str, Optional[str]]]: Список словарей с данными о книгах.
        
    Raises:
        Exception: Если произошла ошибка при парсинге каталога.
    """

    # НАЧАЛО ВАШЕГО РЕШЕНИЯ
    
    base_url = "http://books.toscrape.com/catalogue/"
    all_books_data = []
    page_number = 1
    
    try:
        while True:
            # Формируем URL страницы каталога
            if page_number == 1:
                catalog_url = f"{base_url}page-1.html"
            else:
                catalog_url = f"{base_url}page-{page_number}.html"
            
            print(f"Парсинг страницы {page_number}: {catalog_url}")
            
            # Загружаем страницу каталога
            response = requests.get(catalog_url)
            
            # Проверяем, существует ли страница
            if response.status_code == 404:
                print(f"Страница {page_number} не найдена. Парсинг завершен.")
                break
                
            response.raise_for_status()
            
            # Парсим страницу каталога
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Находим все элементы с книгами
            book_elements = soup.find_all('article', class_='product_pod')
            
            if not book_elements:
                print("На странице не найдено книг. Парсинг завершен.")
                break
            
            # Извлекаем ссылки на страницы книг
            book_urls = []
            for book_element in book_elements:
                link_element = book_element.find('h3').find('a')
                if link_element and link_element.get('href'):
                    # Преобразуем относительную ссылку в абсолютную
                    book_relative_url = link_element['href']
                    # Обрабатываем относительные ссылки
                    if book_relative_url.startswith('../../../'):
                        # Убираем лишние части из пути
                        book_relative_url = book_relative_url.replace('../../../', '')
                    elif book_relative_url.startswith('./'):
                        book_relative_url = book_relative_url.replace('./', '')
                    
                    book_full_url = f"http://books.toscrape.com/catalogue/{book_relative_url}"
                    book_urls.append(book_full_url)
            
            # Парсим данные каждой книги
            for i, book_url in enumerate(book_urls, 1):
                try:
                    print(f"  Парсинг книги {i}/{len(book_urls)}: {book_url}")
                    book_data = get_book_data(book_url)
                    all_books_data.append(book_data)
                    
                    # Добавляем небольшую задержку между запросами
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"    Ошибка при парсинге книги {book_url}: {e}")
                    continue
            
            # Проверяем наличие следующей страницы
            next_button = soup.find('li', class_='next')
            if not next_button:
                print("Следующая страница не найдена. Парсинг завершен.")
                break
                
            page_number += 1
            
            # Добавляем задержку между страницами
            time.sleep(1)
            
    except Exception as e:
        print(f"Произошла ошибка при парсинге каталога: {e}")
        raise
    
    # Сохраняем данные в файл, если указан флаг
    if is_save:
        save_books_to_file(all_books_data)
    
    return all_books_data


def save_books_to_file(books_data: dict) -> None:
    """
    Сохраняет данные о книгах в текстовый файл.
    
    Args:
        books_data (dict): Список с данными о книгах.
    """
    filename = "books_data.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write("ДАННЫЕ О КНИГАХ С SITE BOOKS TO SCRAPE\n")
            file.write("=" * 50 + "\n\n")
            
            for i, book in enumerate(books_data, 1):
                file.write(f"КНИГА #{i}\n")
                file.write("-" * 30 + "\n")
                
                for key, value in book.items():
                    if value is None:
                        value = "Не указано"
                    file.write(f"{key}: {value}\n")
                
                file.write("\n" + "=" * 50 + "\n\n")
        
        print(f"Данные успешно сохранены в файл: {filename}")
        print(f"Всего сохранено книг: {len(books_data)}")
        
    except Exception as e:
        print(f"Ошибка при сохранении в файл: {e}")

    # КОНЕЦ ВАШЕГО РЕШЕНИЯ


# In[6]:


# Проверка работоспособности функции
res = scrape_books(is_save=True) # Допишите ваши аргументы
print(type(res), len(res)) # и проверки


# ## Задание 3. Настройка регулярной выгрузки (10 баллов)
# 
# Настройте автоматический запуск функции сбора данных каждый день в 19:00.
# Для автоматизации используйте библиотеку `schedule`. Функция должна запускаться в указанное время и сохранять обновленные данные в текстовый файл.
# 
# 
# 
# Бесконечный цикл должен обеспечивать постоянное ожидание времени для запуска задачи и выполнять ее по расписанию. Однако чтобы не перегружать систему, стоит подумать о том, чтобы выполнять проверку нужного времени не постоянно, а раз в какой-то промежуток. В этом вам может помочь `time.sleep(...)`.
# 
# Проверьте работоспособность кода локально на любом времени чч:мм.
# 
# 

# In[7]:


# НАЧАЛО ВАШЕГО РЕШЕНИЯ

import schedule
import time

def scheduled_scraping():
    """
    Функция для автоматического запуска парсинга по расписанию
    """
    print(" Запуск автоматического парсинга...")
    
    try:
        # Запускаем парсинг с сохранением в файл
        books_data = scrape_books(is_save=True)
        print(f" Парсинг успешно завершен! Обработано {len(books_data)} книг")
        
    except Exception as e:
        print(f" Ошибка при автоматическом парсинге: {e}")

def run_scheduler(test_time: str = None):
    """
    Запускает планировщик задач
    
    Args:
        test_time (str): Время для тестирования в формате "HH:MM"
    """
    # Настраиваем расписание
    if test_time:
        # Тестовый режим - запуск в указанное время
        print(f" Настроен тестовый запуск в {test_time}")
        schedule.every().day.at(test_time).do(scheduled_scraping)
    else:
        # Режим работы - запуск каждый день в 19:00
        print(" Настроен ежедневный запуск в 19:00")
        schedule.every().day.at("19:00").do(scheduled_scraping)
    
    print(" Планировщик запущен. Ожидание выполнения задач...")
    
    # Бесконечный цикл
    while True:
        schedule.run_pending()
        time.sleep(60)  # Проверяем каждые 60 секунд

# КОНЕЦ ВАШЕГО РЕШЕНИЯ


# ## Задание 4. Написание автотестов (15 баллов)
# 
# Создайте минимум три автотеста для ключевых функций парсинга — например, `get_book_data` и `scrape_books`. Идеи проверок (можете использовать свои):
# 
# * данные о книге возвращаются в виде словаря с нужными ключами;
# * список ссылок или количество собранных книг соответствует ожиданиям;
# * значения отдельных полей (например, `title`) корректны.
# 
# Оформите тесты в отдельном скрипте `tests/test_scraper.py`, используйте библиотеку `pytest`. Убедитесь, что тесты проходят успешно при запуске из терминала командой `pytest`.
# 
# Также выведите результат их выполнения в ячейке ниже.
# 
# **Не забывайте про соблюдение PEP-8**
# 

# In[ ]:


# Ячейка для демонстрации работоспособности
# Сам код напишите в отдельном скрипте
get_ipython().system(' pytest C:\\Users\\dpisarskay001\\Desktop\\hw3\\tests/test_scraper.py')


# In[9]:


# import pytest
# import sys
# import os
# import time

# # Добавляем путь для импорта
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from scraper import BookScraper

# class TestGetBookData:
#     """Тесты для метода get_book_data"""
    
#     def test_returns_dict_with_required_keys(self):
#         """Проверяет, что функция возвращает словарь с нужными ключами"""
        
#         # Создаем экземпляр класса
#         scraper = BookScraper()
        
#         # Используем известную рабочую книгу для тестирования
#         test_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

#         # Добавляем задержку перед запросом
#         time.sleep(1)        

#         # Вызываем метод класса
#         result = scraper.get_book_data(test_url)

#         # Пропускаем тест если нет соединения
#         if result is None:
#             pytest.skip("Нет соединения с сайтом, пропускаем тест")

#         # Проверяем, что результат - словарь
#         assert isinstance(result, dict)
        
#         # Проверяем наличие всех обязательных ключей
#         required_keys = [
#             'title', 'price', 'rating', 'availability', 'description'
#         ]
        
#         for key in required_keys:
#             assert key in result, f"Ключ '{key}' отсутствует в результате"
    
#     def test_book_data_values_correct(self):
#         """Проверяет корректность значений полей"""
#         scraper = BookScraper()
#         test_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
        
#         time.sleep(1)  # Задержка
        
#         result = scraper.get_book_data(test_url)
        
#         if result is None:
#             pytest.skip("Нет соединения с сайтом, пропускаем тест")

#         # Проверяем конкретные значения
#         assert result['title'] == "A Light in the Attic"
#         assert result['url'] == test_url

# class TestScrapeBooks:
#     """Тесты для метода scrape_books"""
    
#     def test_returns_list_of_books(self):
#         """Проверяет, что функция возвращает список книг"""
        
#         scraper = BookScraper()
        
#         # Используем тестовую категорию
#         test_category_url = "http://books.toscrape.com/catalogue/category/books/travel_2/index.html"

#         time.sleep(1)  # Задержка    
    
#         # Вызываем метод с ограничением количества книг
#         result = scraper.scrape_books(test_category_url, max_books=3)
        
#         if 'error' in result:
#             pytest.skip(f"Ошибка при запросе: {result['error']}")

#         # Проверяем структуру результата
#         assert isinstance(result, dict)
#         assert 'books' in result
#         assert 'total_books' in result
        
#         # Проверяем, что books - это список
#         assert isinstance(result['books'], list)
#         assert len(result['books']) > 0
#         assert result['total_books'] == len(result['books'])
    
#     def test_returns_expected_number_of_books(self):
#         """Проверяет, что возвращается ожидаемое количество книг"""
#         scraper = BookScraper()
#         test_category_url = "http://books.toscrape.com/catalogue/category/books/travel_2/index.html"
        
#         # Запрашиваем 2 книги
#         result = scraper.scrape_books(test_category_url, max_books=2)
        
#         assert result['total_books'] == 2
#         assert len(result['books']) == 2
        
#         # Проверяем, что каждая книга - словарь с нужными ключами
#         for book in result['books']:
#             assert isinstance(book, dict)
#             assert 'title' in book
#             assert 'price' in book

# class TestEdgeCases:
#     """Тесты для крайних случаев"""
    
#     def test_invalid_url_handling(self):
#         """Проверяет обработку неверного URL"""
#         scraper = BookScraper()
#         invalid_url = "http://invalid-url-that-does-not-exist.com"
        
#         result = scraper.get_book_data(invalid_url)
        
#         # Проверяем, что возвращается словарь с ошибкой
#         assert isinstance(result, dict)
#         assert 'error' in result
    
#     def test_empty_category(self):
#         """Проверяет обработку пустой категории"""
#         scraper = BookScraper()
#         # Используем несуществующую категорию
#         invalid_category_url = "http://books.toscrape.com/catalogue/category/books/invalid_category/index.html"
        
#         result = scraper.scrape_books(invalid_category_url)
        
#         # Проверяем обработку ошибки
#         assert isinstance(result, dict)
#         assert 'error' in result

# if __name__ == "__main__":
#     # Код выполняется только при прямом запуске файла
#     res = scrape_books(is_save=True)
# else:
#     # При импорте ничего не выполняется
#     pass


# ## Задание 5. Оформление проекта на GitHub и работа с Git (35 баллов)
# 
# В этом задании нужно воспользоваться системой контроля версий Git и платформой GitHub для хранения и управления своим проектом. **Ссылку на свой репозиторий пришлите в форме для сдачи ответа.**
# 
# ### Пошаговая инструкция и задания
# 
# **1. Установите Git на свой компьютер.**
# 
# * Для Windows: [скачайте установщик](https://git-scm.com/downloads) и выполните установку.
# * Для macOS:
# 
#   ```
#   brew install git
#   ```
# * Для Linux:
# 
#   ```
#   sudo apt update
#   sudo apt install git
#   ```
# 
# **2. Настройте имя пользователя и email.**
# 
# Это нужно для подписи ваших коммитов, сделайте в терминале через `git config ...`.
# 
# **3. Создайте аккаунт на GitHub**, если у вас его еще нет:
# [https://github.com](https://github.com)
# 
# **4. Создайте новый репозиторий на GitHub:**
# 
# * Найдите кнопку **New repository**.
# * Укажите название, краткое описание, выберите тип **Public** (чтобы мы могли проверить ДЗ).
# * Не ставьте галочку Initialize this repository with a README.
# 
# **5. Создайте локальную папку с проектом.** Можно в терминале, можно через UI, это не имеет значения.
# 
# **6. Инициализируйте Git в этой папке.** Здесь уже придется воспользоваться некоторой командой в терминале.
# 
# **7. Привяжите локальный репозиторий к удаленному на GitHub.**
# 
# **8. Создайте ветку разработки.** По умолчанию вы будете находиться в ветке `main`, создайте и переключитесь на ветку `hw-books-parser`.
# 
# **9. Добавьте в проект следующие файлы и папки:**
# 
# * `scraper.py` — ваш основной скрипт для сбора данных.
# * `README.md` — файл с кратким описанием проекта:
# 
#   * цель;
#   * инструкции по запуску;
#   * список используемых библиотек.
# * `requirements.txt` — файл со списком зависимостей, необходимых для проекта (не присылайте все из глобального окружения, создайте изолированную виртуальную среду, добавьте в нее все нужное для проекта и получите список библиотек через `pip freeze`).
# * `artifacts/` — папка с результатами парсинга (`books_data.txt` — полностью или его часть, если весь не поместится на GitHub).
# * `notebooks/` — папка с заполненным ноутбуком `HW_03_python_ds_2025.ipynb` и запущенными ячейками с выводами на экран.
# * `tests/` — папка с тестами на `pytest`, оформите их в формате скрипта(-ов) с расширением `.py`.
# * `.gitignore` — стандартный файл, который позволит исключить временные файлы при добавлении в отслеживаемые (например, `__pycache__/`, `.DS_Store`, `*.pyc`, `venv/` и др.).
# 
# 
# **10. Сделайте коммит.**
# 
# **11. Отправьте свою ветку на GitHub.**
# 
# **12. Создайте Pull Request:**
# 
# * Перейдите в репозиторий на GitHub.
# * Нажмите кнопку **Compare & pull request**.
# * Укажите, что было добавлено, и нажмите **Create pull request**.
# 
# **13. Выполните слияние Pull Request:**
# 
# * Убедитесь, что нет конфликтов.
# * Нажмите **Merge pull request**, затем **Confirm merge**.
# 
# **14. Скачайте изменения из основной ветки локально.**
# 
# 
# 
# ### Требования к итоговому репозиторию
# 
# * Файл `scraper.py` с рабочим кодом парсера.
# * `README.md` с описанием проекта и инструкцией по запуску.
# * Папка `artifacts/` с результатом сбора данных (`.txt` файл).
# * Папка `tests/` с тестами на `pytest`.
# * Папка `notebooks/` с заполненным ноутбуком `HW_03_python_ds_2025.ipynb`.
# * Pull Request с комментарием из ветки `hw-books-parser` в ветку `main`.
# * Примерная структура:
# 
#   ```
#   books_scraper/
#   ├── artifacts/
#   │   └── books_data.txt
#   ├── notebooks/
#   │   └── HW_03_python_ds_2025.ipynb
#   ├── scraper.py
#   ├── README.md
#   ├── tests/
#   │   └── test_scraper.py
#   ├── .gitignore
#   └── requirements.txt
#   ```
