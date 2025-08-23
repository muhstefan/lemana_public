import asyncio

from my_libs import AioClient
from my_libs import SingletonMeta
from my_libs import Strategy
from private import *
from private import headers_base


class CompositeData(metaclass=SingletonMeta):
    def __init__(self):
        self.deals_list = []
        self.current_url = None


class Deal:
    # У нас 2 id у сделки. поэтому нужно оба отправлять
    def __init__(self):
        self.project_reference_id = None  # Длинный ID  (id в списке)
        self.presales_id = None  # Короткий ID  (presaleId)
        self.monetary_indicators = {
            "productFact": 0,
            "productPlan": 0,
            "serviceFact": 0,
            "servicePlan": 0,
        }
        self.post_data = {"status": None, "type": "KITCHEN", "updatedBy": "60108582"}


class DealsSorter(Strategy):

    def parse(self):
        if self.get_json and self.get_json.get("content"):  # Есть сделки
            for one_deal in self.get_json.get("content"):
                if one_deal.get("budget"):  # и не пустые совсем
                    self.create_deal(one_deal)
            self.sort_deals()
        else:
            pass

    def create_deal(self, deal):
        new_deal = Deal()
        budget_data = deal.get("budget")
        for key, value in budget_data.items():
            if key in new_deal.monetary_indicators:
                new_deal.monetary_indicators[key] = value
        # Чтобы разделить немного числа и строки (id строка)
        new_deal.project_reference_id = deal.get("id")
        new_deal.presales_id = deal.get("presaleId")
        self.get_main_data.deals_list.append(new_deal)

    def sort_deals(self):
        unsorted_deals = self.get_main_data.deals_list
        for deal in unsorted_deals:
            pr_fact = deal.monetary_indicators["productFact"]
            pr_plan = deal.monetary_indicators["productPlan"]
            sv_fact = deal.monetary_indicators["serviceFact"]
            sv_plan = deal.monetary_indicators["servicePlan"]
            if pr_fact > 10000:  # Есть деньги за товар больше чем 10к
                deal.post_data["status"] = "REGISTRATION"
            elif pr_plan > 0:  # Есть проект, но нет денег
                deal.post_data["status"] = "DEAL_IN_WORK"
            elif sv_fact > 0:  # Нет товаров, но есть услуги
                deal.post_data["status"] = "MEASUREMENT"
            else:
                deal.post_data["status"] = "NEW"


def main_funktion():  # Основная функция

    main_client = AioClient(CompositeData)
    data = CompositeData()
    tasks = main_client.create_tasks_from_number_list(
        list(range(30)), lambda page: CAN_BAN_URL.format(page=page)
    )

    (
        main_client.set_headers(headers_base)
        .set_request_mode(main_client.REQ_MODE_GET_JSON)
        .set_strategy(DealsSorter)
        .set_tasks(tasks)
        .set_certificate(cert_1)
    )

    asyncio.run(main_client.main_asynch())

    tasks = main_client.create_tasks_from_objects(
        data.deals_list,
        lambda deal: PUT_SWITCH_STATUS_DEAL.format(
            presalesId=deal.presales_id, projectReferenceId=deal.project_reference_id
        ),
    )

    main_client.set_tasks(tasks).set_request_mode(main_client.REQ_MODE_PUT)
    asyncio.run(main_client.main_asynch())
