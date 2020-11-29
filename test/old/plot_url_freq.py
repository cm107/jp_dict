from src.refactored.browser_history import BrowserHistory
from logger import logger
from common_utils.time_utils import get_days_elapsed_from_time_usec, get_years_elapsed_from_time_usec
from math import floor
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from common_utils.file_utils import make_dir_if_not_exists

browser_history = BrowserHistory.load_from_path('combined_history.json')

url_targets = [
    'jisho',
    'myanimelist',
    'amazon',
    'gogoanime',
    'animelon',
    'github'
]
url_target_bases = [
    'https://jisho.org/',
    'https://myanimelist.net/',
    'https://www.amazon.co.jp/',
    'https://gogoanime',
    'https://animelon.com/',
    'https://github.com/'
]

save_dir = 'time_elapsed_plot'
make_dir_if_not_exists(save_dir)

for url_target, url_target_base in zip(url_targets, url_target_bases):
    item_list = browser_history.browser_history_item_list.search_by_url_base(url_target_base)
    target_save_dir = f'{save_dir}/{url_target}'
    make_dir_if_not_exists(target_save_dir)

    days_elapsed_freq_dict = {}
    months_elapsed_freq_dict = {}
    years_elapsed_freq_dict = {}

    for i, item in enumerate(item_list):
        days_elapsed = floor(get_days_elapsed_from_time_usec(item.time_usec))
        months_elapsed = floor(get_years_elapsed_from_time_usec(item.time_usec)*12)
        years_elapsed = floor(get_years_elapsed_from_time_usec(item.time_usec))
        if days_elapsed not in days_elapsed_freq_dict:
            days_elapsed_freq_dict[days_elapsed] = 1
        else:
            days_elapsed_freq_dict[days_elapsed] += 1
        if months_elapsed not in months_elapsed_freq_dict:
            months_elapsed_freq_dict[months_elapsed] = 1
        else:
            months_elapsed_freq_dict[months_elapsed] += 1
        if years_elapsed not in years_elapsed_freq_dict:
            years_elapsed_freq_dict[years_elapsed] = 1
        else:
            years_elapsed_freq_dict[years_elapsed] += 1

    days_elapsed_dict = {
        'days_elapsed': [],
        'freq': []
    }
    months_elapsed_dict = {
        'months_elapsed': [],
        'freq': []
    }
    years_elapsed_dict = {
        'years_elapsed': [],
        'freq': []
    }

    for days_elapsed, freq in days_elapsed_freq_dict.items():
        days_elapsed_dict['days_elapsed'].append(days_elapsed)
        days_elapsed_dict['freq'].append(freq)
    for months_elapsed, freq in months_elapsed_freq_dict.items():
        months_elapsed_dict['months_elapsed'].append(months_elapsed)
        months_elapsed_dict['freq'].append(freq)
    for years_elapsed, freq in years_elapsed_freq_dict.items():
        years_elapsed_dict['years_elapsed'].append(years_elapsed)
        years_elapsed_dict['freq'].append(freq)


    days_elapsed_df = pd.DataFrame(days_elapsed_dict)
    months_elapsed_df = pd.DataFrame(months_elapsed_dict)
    years_elapsed_df = pd.DataFrame(years_elapsed_dict)

    sns.barplot(x='days_elapsed', y='freq', data=days_elapsed_df)
    plt.xlabel('Days Elapsed')
    plt.ylabel('Frequency')
    plt.title(f'Frequency of Access to {url_target}')
    plt.savefig(f'{target_save_dir}/days_elapsed.png')
    plt.clf()
    plt.close('all')

    sns.barplot(x='months_elapsed', y='freq', data=months_elapsed_df)
    plt.xlabel('Months Elapsed')
    plt.ylabel('Frequency')
    plt.title(f'Frequency of Access to {url_target}')
    plt.savefig(f'{target_save_dir}/months_elapsed.png')
    plt.clf()
    plt.close('all')

    sns.barplot(x='years_elapsed', y='freq', data=years_elapsed_df)
    plt.xlabel('Years Elapsed')
    plt.ylabel('Frequency')
    plt.title(f'Frequency of Access to {url_target}')
    plt.savefig(f'{target_save_dir}/years_elapsed.png')
    plt.clf()
    plt.close('all')