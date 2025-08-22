from my_libs import SingletonMeta

Message = "Добрый день, вас приветствует менеджер компании Лемана Про, у нас с вами был проект кухни, подскажите он еще актуален?"


class Deal:
    def __init__(self, presales_id, project_reference_id, client_phones=None):
        self.project_reference_id = project_reference_id  # Длинный ID  (id в списке)
        self.presales_id = presales_id  # Короткий ID  (presaleId)
        self.client_phones = client_phones
        self.post_data = {
            "type": "KITCHEN",
            "status": "CANCELLED",
            "reasonToCancel": {"reason": "NOANSWER"},
            "updatedBy": "60079159",
        }


class CompositeData(metaclass=SingletonMeta):
    def __init__(self):
        self._deals = set()  # Список сделок общий
        self._deals_selected = set()  # Список сделок общий

    def get_deals(self):
        return self._deals

    def add_deal(self, deal):
        self._deals.add(deal)

    def add_select_deal(self, deal):
        self._deals_selected.add(deal)

    def get_deals_list(self):
        return self._deals

    def get_selected_deals_list(self):
        return self._deals_selected
