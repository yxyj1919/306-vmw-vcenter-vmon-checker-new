class Person:
    def __init__(self, name):
        self.name = name 

    def sayhi(self):
        print(f"Hi, this is {self.name} speaking.")

    def saybye(self): 
        print(f"Bye, this is {self.name} speaking.")

class Animal:
    def __init__(self, name):
        self.name = name 
    def cat(self):
        print(f" {self.name} is a cat.")

    def dog(self):
        print(f" {self.name} is a dog.")

print(__name__)

if __name__ == "__main__":
    a = Person("Tom")
    a.sayhi()
    a.saybye()
    b = Animal("Tom")
    b.cat()
    b.dog()