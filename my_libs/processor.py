class Strategy:
    def __init__(self, processor_data):
        """
        Конструктор принимает словарь с данными:
        {
            'html': str или None,
            'json': dict или None,
            'post_data': dict или None,
            'url': str,
            'status': int,
            'main_data': класс данных
        }
        """
        self.processor_data = processor_data

    @property
    def get_html(self):
        return self.processor_data.get("html")

    @property
    def get_json(self):
        return self.processor_data.get("json")

    @property
    def get_url(self):
        return self.processor_data.get("url")

    @property
    def get_post_data(self):
        return self.processor_data.get("post_data")

    @property
    def get_status(self):
        return self.processor_data.get("status")

    @property
    def main_data_cls(self):
        # Можно вернуть класс структуры данных, если он нужен в стратегии
        return self.processor_data.get("main_data_cls")

    @property
    def get_main_data(self):
        if self.main_data_cls:
            return self.main_data_cls()
        return None

    @staticmethod
    def _get_data_from_path(data, path):
        keys = path.split(".")
        for key in keys:
            data = data.get(f"{key}")
        return data

    def parse(self):
        """
        Здесь должна быть основная логика парсинга,
        обязательно переопределяется в наследниках.

        По умолчанию — бросаем исключение,
        чтобы точно знать, что метод не реализован.
        """
        raise NotImplementedError("Метод parse() должен быть реализован в наследнике")
