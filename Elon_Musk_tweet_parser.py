import time
import os
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from selenium import webdriver
from auth_data import login, password
import pickle

def create_webdriver_instance():
    """Данная функция создает вебдрайвер Chrome"""
    options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2} # опция отключения загрузки картинок
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    print('create_webdriver_instance - ok')
    return driver

def first_login_to_twitter(login, password, driver):
    """Данная функция нужна для первого запуска Twitter и сохранения данных cookies в файл 'twitter_cookies'."""
    url = 'https://twitter.com/login'
    driver.get(url)
    elem = driver.find_element_by_name('session[username_or_email]')
    elem.send_keys(login)
    elem = driver.find_element_by_name('session[password]')
    elem.send_keys(password)
    elem.send_keys(Keys.ENTER)
    time.sleep(3)
    pickle.dump(driver.get_cookies(), open('twitter_cookies', 'wb'))
    driver.close()
    print('first login - ok')

def go_to_Musk_page(search_term, driver):
    """Функция для входа в Твиттер и перехода на страницу Илона Маска."""
    url = 'https://twitter.com'
    driver.get(url)
    for cookie in pickle.load(open('twitter_cookies', 'rb')):
        driver.add_cookie(cookie)
    driver.refresh()
    driver.implicitly_wait(10)
    driver.get(search_term)
    print('go_to_Musk_page - ok', '\n')
    return True

def scroll_down_page(driver):
    """ Функция прокрутки страницы"""
    last_height = driver.execute_script("return document.body.scrollHeight") # сохраняем текущую высоту
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # прокручиваем
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")  # сохраняем новую высоту
        if new_height == last_height: # сравниваем новую высоту с предыдущей
            break
        last_height = new_height

def collect_all_tweets_from_current_view(driver, num_of_cards, lookback_limit=25):
    """ Данная функция собирает объекты последних подгруженных на страницу твитов. """
    page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]') # собираем объекты твитов подгруженные на страницу в page_cards
    if len(page_cards) <= lookback_limit:
        return page_cards
    else:
        return page_cards[-lookback_limit:]



def extract_data_from_current_tweet_card(card, num_of_card):
    """Данная функция разбирает на части блок твита и выводит результаты на консоль"""
    print(f"Твит номер {num_of_card+1}")
    try:
        user = card.find_element_by_xpath('.//span').text
        print('Автор твита:', user)
    except exceptions.NoSuchElementException:
        user = ""
        print('Автор твита: None')
    except exceptions.StaleElementReferenceException:
        return
    try:
        handle = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
        print('ссылка на автора: ', handle)
    except exceptions.NoSuchElementException:
        handle = ""
        print('ссылка на автора: None')
    try:
        postdate = card.find_element_by_xpath('.//time').get_attribute('datetime')
        print('Дата твита: ', postdate)
    except exceptions.NoSuchElementException:
        print('Дата твита: None')
    try:
        _comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    except exceptions.NoSuchElementException:
        _comment = ""
    try:
        _responding = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    except exceptions.NoSuchElementException:
        _responding = ""
    tweet_text = _comment + _responding
    print('Текст твита: ', tweet_text)
    try:
        reply_count = card.find_element_by_xpath('.//div[@data-testid="reply"]').text
        print('Количество ответов: ', reply_count)
    except exceptions.NoSuchElementException:
        print('Количество ответов: None')
    try:
        retweet_count = card.find_element_by_xpath('.//div[@data-testid="retweet"]').text
        print('Количество ретвитов: ', retweet_count)
    except exceptions.NoSuchElementException:
        print('Количество ретвитов: None')
    try:
        like_count = card.find_element_by_xpath('.//div[@data-testid="like"]').text
        print('Количество лайков: ', like_count, '\n')
    except exceptions.NoSuchElementException:
        print('Количество лайков: None')

def main(login, password, search_term, number_of_twits):
    last_position = None
    end_of_scroll_region = False
    unique_tweets = set()
    if not os.path.exists('./twitter_cookies'): # если программа запущена впервые, то запускается функция first_login_to_twitter, для сохранения куки-файла
        driver = create_webdriver_instance()
        first_login_to_twitter(login, password, driver)
    driver = create_webdriver_instance()
    search_found = go_to_Musk_page(search_term, driver) # функция выполняющая переход на страницу Илона Маска и сохраняющая результат в search_found
    if not search_found:
        return

    num_of_cards = 0
    while num_of_cards < number_of_twits: # внутри данного цикла собираются объекты твитов и разбираются на части. Если достигаем нужного количества собранных твитов цикл прерывается
        cards = collect_all_tweets_from_current_view(driver, num_of_cards)  # собираем объекты твитов в переменную cards
        for card in cards:
            try:
                tweet = extract_data_from_current_tweet_card(card, num_of_cards) # разбираем твит на составляющие части
                num_of_cards += 1
                if num_of_cards == number_of_twits:
                    break
            except exceptions.StaleElementReferenceException:
                continue
            if not tweet:
                continue
        scroll_down_page(driver)
    driver.quit()
    print(f'Собрано {num_of_cards} твитов')


if __name__ == '__main__':
    usr = login
    pwd = password
    term = 'https://twitter.com/elonmusk'
    number_of_twits = 20
    main(usr, pwd, term, number_of_twits)
