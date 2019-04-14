# otus_python_hw1
ДЗ №3

## Scoring API

Запуск из папки ./scoring

python api.py

### Добавление нового метода обработки
Для добавления нового метода  необходимо создать класс, наследующийся от `Request`, по имеющемуся шаблону

`coprocessor_name` - название метода

`field1, field2...` - поля метода, экземпляры классов-наследников `Field`

`validate` - функция проверки переданных параметов

`process` - функция обработки

```
Coprocessor simple template
@coprocessor(MethodRequest)
class SimpleCoprocessor(Request):
    coprocessor_name = "simple"
    field1 = CharField(required=True, nullable=False)
    field2 = EmailField(required=True, nullable=False)
    def validate(self):
        base_validation = super().validate()
        if not base_validation.is_valid:
            return base_validation
        # check something
        if not (self.field1 == "42" and self.field2 == "admin@admin.admin"):
            return validation_res(False, "something wrong")
        return validation_res(True, "")
    def process(self):
        res = super().process()
        if res:
            return res
        # do something
        res = f"your choice is {self.field1}"
        return res, OK
```
