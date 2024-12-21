# настройки:

product_col_names = ['товар', 'название', 'наименование', 'продукт']

price_col_names = ['розница', 'цена']

weight_col_names = ['вес', 'масса', 'фасовка']

output_header_html = '''<!DOCTYPE html>
<html>
    <head>
        <title>Позиции продуктов</title>
    </head>
    <body>
        <table>
            <tr>
                <th>Номер</th>
                <th>Название</th>
                <th>Цена</th>
                <th>Фасовка</th>
                <th>Файл</th>
                <th>Цена за кг.</th>
            </tr>
'''