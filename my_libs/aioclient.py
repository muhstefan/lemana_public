import asyncio
import ssl

import aiohttp


class TaskObject:
    """Объект на базе которого будем делать запрос"""

    def __init__(self, url, post_data=None):
        self.url = url
        self.post_data = post_data


class AioClient:
    """Клиент работающий в зависимости от режима (пост гет и тд)"""

    REQ_MODE_POST = "post"
    REQ_MODE_PUT = "put"
    REQ_MODE_PATCH = "patch"
    REQ_MODE_DELETE = "delete"
    REQ_MODE_GET_HTML = "get_html"
    REQ_MODE_GET_JSON = "get_json"

    def __init__(self, main_data_name):  # Принимаем название комбинатора
        self._main_data_name = main_data_name  # Ссылка на singletone класс данных
        self._strategy = None
        self._tasks = None
        self._session = None
        self._headers = None
        self._req_mode = None
        self._certificate = None
        self._ssl_context = None

    async def main_asynch(self):
        await self._create_ssl_session(self._certificate)
        async with self._session:
            if len(self._tasks) == 1:
                await self._fetch_deal(self._get_one_task())
            else:
                tasks = self._group_request()
                await asyncio.gather(*tasks)

    async def _fetch_deal(self, task: TaskObject):
        task_url = task.url
        task_post_data = task.post_data
        if self._req_mode == self.REQ_MODE_POST:
            async with self._session.post(
                task_url, headers=self._headers, json=task_post_data
            ) as response:
                return await self._process_response(
                    response=response, url=task_url, post_data=task_post_data
                )
        elif self._req_mode == self.REQ_MODE_PUT:
            async with self._session.put(
                task_url, headers=self._headers, json=task_post_data
            ) as response:
                return await self._process_response(
                    response=response, url=task_url, post_data=task_post_data
                )
        elif self._req_mode == self.REQ_MODE_DELETE:
            async with self._session.delete(
                task_url, headers=self._headers
            ) as response:
                return await self._process_response(response=response, url=task_url)
        elif self._req_mode == self.REQ_MODE_PATCH:
            async with self._session.patch(
                task_url, headers=self._headers, json=task_post_data
            ) as response:
                return await self._process_response(
                    response=response, url=task_url, post_data=task_post_data
                )
        else:
            async with self._session.get(task_url, headers=self._headers) as response:
                return await self._process_response(response=response, url=task_url)

    async def _process_response(self, response, url, post_data=None):

        status = response.status
        json_data = None
        html_data = None

        # Замерить увеличит для время работы если сделать обязательный
        # html_data = await response.text()

        if (
            self._req_mode == self.REQ_MODE_GET_HTML
            or self._req_mode == self.REQ_MODE_PUT
            or self._req_mode == self.REQ_MODE_PATCH
        ):
            html_data = await response.text()
        elif self._req_mode == self.REQ_MODE_GET_JSON:
            json_data = await response.json()

        self.parse_with_strategy(
            html=html_data,
            json=json_data,
            post_data=post_data,
            url=url,
            status=status,
            main_data=self._main_data_name,  # передаем синглтон
            strategy_cls=self._strategy,
        )

    # Вспомогательная функция для вызова стратегии
    @staticmethod
    def parse_with_strategy(
        html=None,
        json=None,
        url=None,
        status=None,
        main_data=None,
        strategy_cls=None,
        post_data=None,
    ):
        if strategy_cls is None:
            raise ValueError("strategy_cls must be provided")

        processor_data = {
            "html": html,
            "json": json,
            "post_data": post_data,
            "url": url,
            "status": status,
            "main_data_cls": main_data,
        }
        strat_instance = strategy_cls(processor_data)
        return strat_instance.parse()

    """Эти 2 функции позволяют удобно создавать списки задач, принимая список чего-либо и функцию модификации url"""

    @staticmethod
    def create_tasks_from_objects(list_of_objects, url_function):
        tasks = []
        for obj in list_of_objects:
            post_data = obj.post_data
            url = url_function(obj)
            task = TaskObject(url=url, post_data=post_data)
            tasks.append(task)
        return tasks

    @staticmethod
    def create_tasks_from_number_list(number_list, url_function):
        tasks = []
        for one in number_list:
            url = url_function(one)
            task = TaskObject(url=url, post_data=None)
            tasks.append(task)
        return tasks

    def _get_one_task(self):
        return self._tasks.pop(0)

    def _group_request(self):
        tasks = []
        for task in self._tasks:
            # Добавляем задачу в список И НЕ ВЫПОЛНЯЕМ ЕЕ
            tasks.append(self._fetch_deal(task))
        return tasks

    def set_request_mode(self, req_mode):
        self._req_mode = req_mode
        return self

    def set_tasks(self, tasks):
        self._tasks = tasks
        return self

    def set_task(self, task):
        self._tasks = [task]
        return self

    def set_strategy(self, strategy):
        self._strategy = strategy
        return self

    def set_headers(self, headers):
        self._headers = headers
        return self

    def set_certificate(self, certificate):
        self._certificate = certificate
        return self

    def get_data(self):
        return self._main_data_name()

    async def _create_ssl_session(self, certificate):
        ssl_context = ssl.create_default_context()  # Создаем SSL-контекст
        ssl_context.load_verify_locations(cadata=certificate)
        connector = aiohttp.TCPConnector(ssl=ssl_context)  # Создаем TCP-коннектор с SSL
        self._session = aiohttp.ClientSession(connector=connector)
