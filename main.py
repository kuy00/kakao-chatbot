from typing import Dict, Any
from fastapi import FastAPI, BackgroundTasks
import requests
from naver import Naver
from dateutil.relativedelta import relativedelta
from datetime import datetime

app = FastAPI()


def callback_request(user_message: str, callback_url: str):
    print(f'callback url : {callback_url}')
    if callback_url != '':
        # 네이버 키워드 검색량 조회
        search_keyword_payload = {
            'hintKeywords': user_message,
            'showDetail': '1',
        }
        keyword_statistics_list = Naver.call_api('GET', '/keywordstool', search_keyword_payload)

        print(f'search keyword : {keyword_statistics_list}')

        keyword_statistics = keyword_statistics_list['keywordList'][0]
        total_count = keyword_statistics['monthlyPcQcCnt'] + keyword_statistics['monthlyMobileQcCnt']
        callback_payload = {
            'version': '2.0',
            'data': {
                'keyword': user_message,
                'total_count': f'{total_count:,}',
                'pc_count': f"{keyword_statistics['monthlyPcQcCnt']:,}",
                'mobile_count': f"{keyword_statistics['monthlyMobileQcCnt']:,}",
                'pc_ratio': round(keyword_statistics['monthlyPcQcCnt'] / total_count * 100, 1),
                'mobile_ratio': round(keyword_statistics['monthlyMobileQcCnt'] / total_count * 100, 1),
                'start_date': (datetime.now() - relativedelta(months=1, days=1)).strftime('%Y-%m-%d'),
                'end_date': (datetime.now() - relativedelta(days=1)).strftime('%Y-%m-%d'),
            }
        }
        response = requests.post(callback_url, json=callback_payload)
        print(f'callback response : {response.json()}')


@app.post("/")
async def chatbot(request: Dict[str, Any], background_tasks: BackgroundTasks):
    user_request = request['userRequest'] if 'userRequest' in request else {}
    user_message = user_request['utterance'] if 'utterance' in user_request else ''
    callback_url = user_request['callbackUrl'] if 'callbackUrl' in user_request else ''

    print(f'request : {request}')

    skill_response = {
        'version': '2.0',
        'useCallback': True,
        'data': {
            'text': '처리 중...'
        }
    }

    background_tasks.add_task(
        callback_request,
        user_message,
        callback_url
    )

    return skill_response


@app.get('/naver')
def naver(keyword: str):
    payload = {
        'hintKeywords': keyword,
        'showDetail': '1',
    }
    response = Naver.call_api('GET', '/keywordstool', payload)
    return response
