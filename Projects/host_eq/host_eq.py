import asyncio
from datetime import datetime
from my_libs import AioClient, TaskObject, Strategy
from private import cert_1, url_EQ, headersEQ
from projects.host_eq.data import CompositeData, Appointment, instruction


class EqRequester(Strategy):

    spp_name_filter = None

    def parse(self):
        for resource in self.get_json.get("resources", []):
            if not resource.get("appointments"):
                continue
            spp_name = resource.get("title")
            if (EqRequester.spp_name_filter is None) or (
                EqRequester.spp_name_filter in spp_name.lower()
            ):
                appointments = CompositeData().appointments
                for appointment in resource.get("appointments", []):
                    phone = appointment.get("phone")
                    client_name = appointment.get("customerName")
                    time = appointment.get("plannedStartedAt")
                    dt = datetime.fromisoformat(time).strftime("%H:%M")
                    if phone and client_name:
                        appointment = Appointment(
                            spp_name=spp_name,
                            client_name=client_name,
                            phone=phone,
                            time=dt,
                        )
                        appointments.append(appointment)


def main_function():

    data = CompositeData()

    mode_and_time = input(instruction).split(" ")
    time = mode_and_time[0]

    if len(mode_and_time) not in (1, 2):
        return

    if len(mode_and_time) == 2 and mode_and_time[1]:
        EqRequester.spp_name_filter = mode_and_time[1].lower()

    main_client = AioClient(CompositeData)
    url = url_EQ.format(time=time)
    task = TaskObject(url=url)

    (
        main_client.set_task(task)
        .set_certificate(cert_1)
        .set_request_mode(main_client.REQ_MODE_GET_JSON)
        .set_strategy(EqRequester)
        .set_headers(headersEQ)
    )

    asyncio.run(main_client.main_asynch())

    for appointment in data.appointments:
        print(appointment)

    input("Press Enter to close")


main_function()
