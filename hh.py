import requests
import os
from dotenv import load_dotenv
from terminaltables import AsciiTable


def create_table(table, title):
    table_data = [
        [
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата'
        ]
    ]

    for language, info in table.items():
        table_data.append([
            language,
            info['vacancies_found'],
            info['vacancies_processed'],
            info['average_salary']
        ])
    
    return AsciiTable(table_data)

def predict_rub_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        return None
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from and not salary_to:
        return salary_from * 1.2
    elif not salary_from and salary_to:
        return salary_to * 0.8


def find_jobs_hh():
    jobs_hh = dict()
    programming_languages = [
        "javaScript",
        "java" ,
        "python" ,
        "ruby" ,
        "c++" ,
        "c#" ,
        "c" ,
        "go" 
    ]

    for language in programming_languages:
        url = 'https://api.hh.ru/vacancies'
        vacancies_found = 0
        salaries = []
        page = 0
        moscow_area_id = 1
        days_period = 30
        vacancies_per_page = 100

        while True:
            params = {
                'text': f'программист {language}',
                'area': moscow_area_id,
                'period': days_period,
                'per_page': vacancies_per_page,
                'page': page
            }
            response = requests.get(url, params=params)
            response.raise_for_status()

            vacancies_from_page = response.json()
            vacancies_found = vacancies_from_page['found']

            for vacancy in vacancies_from_page['items']:
                salary_values = vacancy.get('salary')
                if salary_values and salary_values.get('currency') == 'RUR':
                    salary_from = salary_values.get('from')
                    salary_to = salary_values.get('to')
                    salary = predict_rub_salary(salary_from, salary_to)
                    if salary:
                        salaries.append(salary)

            if page + 1 >= vacancies_from_page['pages']:
                break

            page += 1

        job_and_salary = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': len(salaries),
            'average_salary': int(sum(salaries) / len(salaries)) if salaries else 0
        }

        jobs_hh[language] = job_and_salary

    return jobs_hh


def predict_rub_salary_sj(current_vacancie):
    currency = current_vacancie["currency"]
    if currency != "rub":
        return None
    salary_from = current_vacancie["payment_from"]
    salary_to = current_vacancie["payment_to"]
    return predict_rub_salary(salary_from, salary_to)


def find_jobs_superjob(secret_key):
    jobs_superjob = dict()
    programming_languages = [
        "javaScript",
        "java" ,
        "python" ,
        "ruby" ,
        "c++" ,
        "c#" ,
        "c" ,
        "go" 
    ]
    
    for language in programming_languages:
        url= 'https://api.superjob.ru/2.0/vacancies/'
        page = 0
        moscow_town = 4
        category = 48
        vacacies_per_page = 100
        vacancies_found = 0
        salaries = []

        while True:
            headers = {
                'X-Api-App-Id': secret_key,
            }
            params = {
                'town': moscow_town,
                'catalogues': category,
                'keyword': {language},
                'count': vacacies_per_page,
                'page': page
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            vacancies_response = response.json()
            vacancies_from_page = vacancies_response['objects']
            vacancies_found = vacancies_response['total']

            if not vacancies_from_page:
                break

            for vacancy in vacancies_from_page:
                salary =  predict_rub_salary_sj(current_vacancie)
                 if salary:
                    salaries.append(salary)
            page += 1

        if salaries:
            average_salary = sum(salaries) / len(salaries)
        else:
            average_salary = 0

        jobs_superjob[language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': len(salaries),
            'average_salary': average_salary
        }
    return jobs_superjob


if __name__ == '__main__':
    load_dotenv()
    secret_key = os.environ['SUPERJOB_KEY']
    
    hh_table = find_jobs_hh()
    superjob_table = find_jobs_superjob(secret_key)

    print(create_table(hh_table, 'HH Moscow'))
    print(create_table(superjob_table, 'SuperJob Moscow'))
