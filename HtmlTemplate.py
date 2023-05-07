class HtmlTemplate:
        # создание файл отчёта
        @staticmethod
        def create_file(trs, description, countAll, countErrors, countSuccess):     
           template = []
           template.append(f""" <!DOCTYPE html>
                                    <html lang="en">
                                    <head>
                                        <meta charset="UTF-8">
                                        <meta http-equiv="X-UA-Compatible" content="IE=edge">
                                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                        <title>Document</title>
                                        <style>
                                            table {{
                                                border: black solid 1px;
                                                margin: auto;
                                                margin-top: 20px;
                                                border-collapse: collapse; 
                                            }}
                                            td, tr {{
                                                padding: 3px; 
                                                border: 1px solid black; 
                                            }}
                                        </style>
                                    </head>
                                    <body>
                                    <table>
                                    <tr>
                                        <td>Текст отправки</td>
                                        <td>{description}</td>
                                        <td>Отправлено:<br>{countAll}</td>
                                        <td>Успешных:<br>{countSuccess}</td>
                                        <td style="width: 100px;">Не успешных:<br>{countErrors}</td>
                                    </tr>
                                    <tr>
                                        <td>ID чата</td>
                                        <td>Статус</td>
                                    </tr>
                                """)
           for tr in trs:
                template.append(tr)

           template.append(""" </table>
                            </table>
                            </body>
                            </html> """)    
           return ''.join(template)
        
        # создание строки для таблицы
        @staticmethod
        def create_line_table(idTg, result):
             return f"<tr><td>{idTg}</td><td>{result}</td></tr>"