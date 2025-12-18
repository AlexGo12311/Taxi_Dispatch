import requests


class FlaskAPIClient:
    BASE_URL = 'http://localhost:5003'

    @classmethod
    def get_statistics(cls):
        try:
            response = requests.get(f"{cls.BASE_URL}/api/taxi/statistics", timeout=5)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка подключения к Flask: {e}")
            return {'success': False, 'error': f'Не удалось подключиться к Flask на {cls.BASE_URL}'}
        except Exception as e:
            print(f"Другая ошибка: {e}")
            return {'success': False, 'error': str(e)}
        return {'success': False, 'error': 'Неизвестная ошибка'}

    @classmethod
    def get_orders(cls, status=None):
        try:
            params = {}
            if status:
                params['status'] = status

            response = requests.get(
                f"{cls.BASE_URL}/api/taxi/orders",
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'error': f'API вернул код {response.status_code}'
                }

        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': f'Flask сервер не запущен на {cls.BASE_URL}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @classmethod
    def test_connection(cls):
        try:
            response = requests.get(f"{cls.BASE_URL}/health", timeout=2)
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None
            }
        except:
            return {'success': False, 'error': 'Нет подключения'}