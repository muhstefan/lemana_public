import asyncio

from my_libs import Strategy, AioClient
from data import *
from private import *
import pandas as pd

from projects.spp_rate.time_module import SppRateTime


class DealList(Strategy):

    def parse(self):
        self._get_parsed_data()

    def _get_parsed_data(self):  # Все сделки 1 спп
        one_client_phones = []

        externalId = self.get_json.get("customer", {}).get("externalId", {})
        for block in externalId.get("communications", {}):
            if block.get("type") == "PHONENUMBER":
                phone_1 = block.get("value")
                one_client_phones.append(phone_1)

        phone_2 = self.get_json.get("customer", {}).get("phone")
        project_reference_id = self.get_json.get("projectReferenceId")
        one_client_phones.append(phone_2)
        new_deal = Deal(
            project_reference_id=project_reference_id,
            client_phones=one_client_phones,
            presales_id=None,
        )
        self.get_main_data.add_deal(new_deal)


class EqRequester(Strategy):

    def parse(self):
        self._eq_check()

    # Делаем все тоже что и в процессорах. Как будто, получаем доступ к данным
    def _eq_check(self):
        for one_deal in self.get_json.get("content", []):
            # Если сделка не завершена и не отменена
            if one_deal.get("status") not in ("CANCELLED", "DEAL_COMPLETED"):
                # Если нет клиента
                if not one_deal.get("customer"):
                    continue
                phone = one_deal.get("customer").get("phone")
                self.get_main_data.add_phone(phone)


class CustomReq(Strategy):

    def parse(self):
        self._eq_check()

    # Делаем все тоже что и в процессорах. Как будто, получаем доступ к данным
    def _eq_check(self):
        for one_deal in self.get_json.get("content", []):
            # Если сделка не завершена и не отменена
            if one_deal.get("status") not in ("CANCELLED", "DEAL_COMPLETED"):

                project_reference_id = one_deal.get("id")
                presales_id = one_deal.get("presaleId")
                new_deal = Deal(
                    presales_id=presales_id, project_reference_id=project_reference_id
                )
                self.get_main_data.add_deal(new_deal)


class CustomReq2(Strategy):

    def parse(self):
        self._get_parsed_data()

    def _get_parsed_data(self):  # Все сделки 1 спп
        date = self.get_json.get("createdDate")
        check = SppRateTime.check_time_before_may_2025(date)
        if check:
            presales_id = self.get_json.get("interestId")
            project_reference_id = self.get_json.get("projectReferenceId")
            new_selected_deal = Deal(
                presales_id=presales_id, project_reference_id=project_reference_id
            )
            new_selected_deal.post_data["status"] = "CANCELLED"
            self.get_main_data.add_select_deal(new_selected_deal)


class CustomPass(Strategy):

    def parse(self):
        pass


def take_deals_from_spp(ldap_spp):  # Основная функция

    main_client = AioClient(CompositeData)

    tasks = main_client.create_tasks_from_number_list(
        list(range(6)), lambda page: url_deals_spp_list.format(page=page, ldap=ldap_spp)
    )

    (
        main_client.set_tasks(tasks)
        .set_certificate(cert_2)
        .set_headers(headersEQ)
        .set_request_mode(main_client.REQ_MODE_GET_JSON)
        .set_strategy(EqRequester)
    )

    asyncio.run(main_client.main_asynch())

    with open("Phones.txt", "w", encoding="utf-8") as file:
        for number in main_client.get_data().get_phones():
            mask_string = f"{number} % {Message}"
            file.write(mask_string + "\n")


def take_deals_from_canceled_in_exel():
    deals_id = read_deal_ids_from_excel("отмены кухни")
    main_client = AioClient(CompositeData)
    tasks = main_client.create_tasks_from_number_list(
        deals_id, lambda deal_id: url_deal_information.format(deal_id=deal_id)
    )

    (
        main_client.set_tasks(tasks)
        .set_certificate(cert_2)
        .set_headers(headersEQ)
        .set_request_mode(main_client.REQ_MODE_GET_JSON)
        .set_strategy(DealList)
    )

    asyncio.run(main_client.main_asynch())
    save_deals_to_excel(main_client.get_data().get_deals())


def read_deal_ids_from_excel(
    file_name: str, sheet_name: str = "Лист1", header_rows: int = 1
) -> list:
    file_path = f"{file_name}.xlsx"
    df = pd.read_excel(
        file_path, sheet_name=sheet_name, header=None, skiprows=header_rows
    )
    deal_id_list = df[0].tolist()
    return deal_id_list


def save_deals_to_excel(deals, file_name="output_deals.xlsx", sheet_name="Sheet1"):
    rows = []
    for deal in deals:
        deal_id = deal.deal_id
        for phone in deal.client_phones:
            rows.append({"deal_id": deal_id, "phone": phone})

    df = pd.DataFrame(rows)
    df.to_excel(file_name, index=False, sheet_name=sheet_name)
    print(f"Данные сохранены в файл {file_name}")


def custom(ldap_spp):  # Основная функция

    main_client = AioClient(CompositeData)
    data = CompositeData()
    tasks = main_client.create_tasks_from_number_list(
        list(range(6)), lambda page: url_deals_spp_list.format(page=page, ldap=ldap_spp)
    )

    (
        main_client.set_tasks(tasks)
        .set_certificate(cert_2)
        .set_headers(headersEQ)
        .set_request_mode(main_client.REQ_MODE_GET_JSON)
        .set_strategy(CustomReq)
    )

    asyncio.run(main_client.main_asynch())
    deals = data.get_deals_list()

    tasks = main_client.create_tasks_from_objects(
        deals,
        lambda deal: url_deal_information.format(deal_id=deal.project_reference_id),
    )

    main_client.set_tasks(tasks).set_strategy(CustomReq2)

    asyncio.run(main_client.main_asynch())

    tasks = main_client.create_tasks_from_objects(
        main_client.get_data().get_selected_deals_list(),
        lambda deal: PUT_SWITCH_STATUS_DEAL.format(
            presalesId=deal.presales_id, projectReferenceId=deal.project_reference_id
        ),
    )

    main_client.set_tasks(tasks).set_request_mode(
        main_client.REQ_MODE_PUT
    ).set_strategy(CustomPass)
    asyncio.run(main_client.main_asynch())
