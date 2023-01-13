import random
import sys

from locust import HttpUser, SequentialTaskSet, task, between
from bs4 import BeautifulSoup
import warnings

from locust.exception import StopUser

warnings.filterwarnings("ignore")


class CredentialLoadTest(SequentialTaskSet):
    Data = {"phone": "11111111111", "password": "22222"}
    token = ""
    verify = False
    list_category = []
    list_subcategory = []
    list_items = []
    offer_json = []
    city_json = []

    @task
    def open_page(self):
        r1 = self.client.get("/ru/", verify=self.verify)
        print("Page:", r1.url)
        soup = BeautifulSoup(r1.text, 'html.parser')
        self.token = soup.find('meta', {'name': 'csrf-token'})['content']
        category = soup.find("nav").find("ul")
        for link in category.find_all("li"):
            self.list_category.append(link.find("a")["href"])
            if link.find("ul") is not None:
                for subcategory in link.find("ul"):
                    if subcategory != '\n':
                        for i in subcategory.find_all("li"):
                            self.list_subcategory.append(i.find("a")["href"])
        r2 = self.client.get("/ru/product/viewed/", verify=self.verify)
        print("Page:", r2.url)
        r3 = self.client.get("/ru/cart/items/", verify=self.verify)
        print("Page:", r3.url)
        r4 = self.client.get("/ru/cities/", verify=self.verify).json()
        print("Page:", r4)
        for city in r4:
            self.city_json.append(city["id"])
        r5 = self.client.get("/ru/cart/average-products/", verify=self.verify)
        print("Page:", r5.url)
        r6 = self.client.get("/ru/products/combine/", verify=self.verify)
        print("Page:", r6.url)

    @task
    def login(self):
        resp = self.client.post("/ru/ajax-login/", verify=self.verify, data=self.Data, headers={
            "Content-Type": "multipart/form-data", "X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token}
                                )
        print("Token:", resp.url)
        if resp.status_code != 200:
            print("Failed to authenticate.")
            sys.exit()

    @task
    def random_category(self):
        category = random.choice(self.list_category)
        resp = self.client.get(f"/ru{category}", verify=self.verify)
        resp1 = self.client.get(f"/ru{category}ajax-reviews/", verify=self.verify)
        print("Category:", resp.url)
        print("Category:", resp1.url)

    @task
    def random_subcategory(self):
        subcategory = random.choice(self.list_subcategory)
        resp = self.client.get(f"/ru{subcategory}", verify=self.verify)
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.find_all("div", class_="product-item")
        if len(items):
            for div in items:
                link = div.find("a", class_="product-item__image")
                if link and link["href"]:
                    self.list_items.append(link["href"])
        resp1 = self.client.get(f"/ru{subcategory}ajax-reviews/", verify=self.verify)
        print("Subcategory:", resp.url)
        print("Subcategory:", resp1.url)

    @task
    def random_item(self):
        item = random.choice(self.list_items)
        number_item = item.split("/")[2]
        resp = self.client.get(f"/ru{item}", verify=False)
        print("Item:", resp.url)
        resp1 = self.client.get(f"/ru{item}offers/", verify=False).json()
        print("Item:", resp1)
        for offer in resp1:
            self.offer_json.append(offer["product_id"])
        resp2 = self.client.get(f"/ru{item}details/", verify=False)
        print("Item:", resp2.url)
        resp3 = self.client.get("/ru/reviews/types-list/", verify=False)
        print("Item:", resp3.url)
        resp4 = self.client.get("/ru/reviews/list/", verify=False, params={"product_id": number_item})
        print("Item:", resp4.url)
        resp5 = self.client.get("/ru/questions/list/", verify=False, params={"product_id": number_item})
        print("Item:", resp5.url)

    @task
    def add_item(self):
        resp = self.client.post("/ru/cart/add/}", verify=False, data={"offer_id": self.offer_json, "quantity": "1",
                                                                      "stats": "{}"},
                                headers={"X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token})
        print("Add item:", resp.url)

    @task
    def order(self):
        city = random.choice(self.city_json)
        resp = self.client.get("/ru/order/", verify=False)
        print("Order:", resp.url)
        resp1 = self.client.post("/ru/order/api/bonus/", verify=False, data={"phone": self.Data["phone"]},
                                 headers={"X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token})
        print("Order:", resp1.url)
        resp2 = self.client.get("/ru/order/api/user-data/", verify=False)
        print("Order:", resp2.url)
        resp3 = self.client.post("/ru/order/api/last-profile/", verify=False, data={"phone": self.Data["phone"]},
                                 headers={"X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token})
        print("Order:", resp3.url)
        resp4 = self.client.post("/ru/order/api/delivery-list/", verify=False, data={"cityId": city},
                                 headers={"X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token}).json()
        print("Order:", resp4)
        delivery_id = resp4[0]["value"]
        resp5 = self.client.post("/ru/order/api/delivery/", verify=False, data={"phone": self.Data["phone"],
                                                                                "cityId": city,
                                                                                "deliveryId": delivery_id},
                                 headers={"X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token})
        print("Order:", resp5.url)
        resp6 = self.client.post("/ru/order/api/totals/", verify=False, data={"phone": self.Data["phone"],
                                                                              "cityId": city,
                                                                              "deliveryId": delivery_id},
                                 headers={"X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token})
        print("Order:", resp6.url)
        resp7 = self.client.post("/ru/order/api/paysystem-list/", verify=False, data={"deliveryId": delivery_id},
                                 headers={"X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token})
        print("Order:", resp7.url)

    @task
    def done(self):
        raise StopUser()


class AwesomeUser(HttpUser):
    tasks = [CredentialLoadTest]
    host = "https://avocado.ua"
    wait_time = between(5, 9)
