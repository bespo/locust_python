import sys
import random
from bs4 import BeautifulSoup
from locust import HttpUser, TaskSet, task, between


class User(HttpUser):
    @task
    class Tasks(TaskSet):
        host = "https://avocado.ua"
        wait_time = between(1, 5)
        Data = {"phone": "0963239338", "password": "qwerty_123"}
        token = ""
        list_category = []
        list_subcategory = []
        list_items = []
        offer_json = []
        city_json = []

        @task
        def open_page(self):
            resp = self.client.get("/ru/", verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')
            self.token = soup.find('meta', {'name': 'csrf-token'})['content']
            category = soup.find("nav").find("ul")
            for link in category.find_all("li"):
                self.list_category.append(link.find("a")["href"])
                if link.find("ul") is not None:
                    for subcategory in link.find("ul"):
                        for i in subcategory.find_all("li"):
                            self.list_subcategory.append(i.find("a")["href"])
            self.client.get("/ru/product/viewed/", verify=False)
            self.client.get("/ru/cart/items/", verify=False)
            resp3 = self.client.get("/ru/cities/", verify=False).json()
            for city in resp3:
                self.city_json.append(city["id"])
            self.client.get("/ru/cart/average-products/", verify=False)
            self.client.get("/ru/products/combine/", verify=False)
            print("Page:", resp.url)

        @task
        def login(self):
            resp = self.client.post("/ru/ajax-login/", verify=False, data=self.Data, headers={
                "Content-Type": "multipart/form-data", "X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token}
                                    )
            if resp.status_code != 200:
                print("Failed to authenticate.")
                print("Token:", resp.url)
                sys.exit()

        @task
        def random_category(self):
            category = random.choice(self.list_category)
            resp = self.client.get(f"/ru{category}", verify=False)
            self.client.get(f"/ru{category}ajax-reviews/", verify=False)
            print("Category:", resp.url)
            print("Category:", resp.request.body)

        @task
        def random_subcategory(self):
            subcategory = random.choice(self.list_subcategory)
            resp = self.client.get(f"/ru{subcategory}", verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for div in soup.find_all("div", class_="product-item"):
                self.list_items.append(div.find("a", class_="product-item__image")["href"])
            self.client.get(f"/ru{subcategory}ajax-reviews/", verify=False)
            print("Subcategory:", resp.url)
            print("Subcategory:", resp.request.body)

        @task
        def random_item(self):
            item = random.choice(self.list_items)
            number_item = item.split("/")[2]
            resp = self.client.get(f"/ru{item}", verify=False)
            self.client.get(f"/ru{item}offers/", verify=False).json()
            for offer in resp:
                self.offer_json.append(offer["product_id"])

            self.client.get(f"/ru{item}details/", verify=False)
            self.client.get("/ru/reviews/types-list/", verify=False)
            resp1 = self.client.get("/ru/reviews/list/", verify=False, params={"product_id": number_item})
            self.client.get("/ru/questions/list/", verify=False, params={"product_id": number_item})
            print("Item:", resp.url)
            print("Item:", resp.request.body)
            print("Item:", resp1.url)
            print("Item:", resp1.request.body)

        @task
        def add_item(self):
            resp = self.client.post("/ru/cart/add/}", verify=False, data={"offer_id": self.offer_json, "quantity": "1",
                                                                          "stats": "{}"},
                                    headers={"X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token})
            print("Add item:", resp.url)
            print("Add item:", resp.request.body)

        @task
        def order(self):
            city = random.choice(self.city_json)
            resp = self.client.get("/ru/order/", verify=False)
            self.client.post("/ru/order/api/bonus/", verify=False, data={"phone": self.Data["phone"]},
                             headers={"X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token})
            self.client.get("/ru/order/api/user-data/", verify=False)
            self.client.post("/ru/order/api/last-profile/", verify=False, data={"phone": self.Data["phone"]},
                             headers={"X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token})
            resp5 = self.client.post("/ru/order/api/delivery-list/", verify=False, data={"cityId": city},
                                     headers={"X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token}).json()
            delivery_id = resp5[0]["value"]
            self.client.post("/ru/order/api/delivery/", verify=False, data={"phone": self.Data["phone"], "cityId": city,
                                                                            "deliveryId": delivery_id},
                             headers={"X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token})
            self.client.post("/ru/order/api/totals/", verify=False, data={"phone": self.Data["phone"], "cityId": city,
                                                                          "deliveryId": delivery_id},
                             headers={"X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token})
            self.client.post("/ru/order/api/paysystem-list/", verify=False, data={"deliveryId": delivery_id},
                             headers={"X-REQUESTED-WITH": "XMLHttpRequest", "X-CSRF-TOKEN": self.token})
            print("Order:", resp.url)
