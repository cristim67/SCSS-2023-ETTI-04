import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import easyocr
import mysql.connector
import util
import geocoder
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="parcare"
)
server = smtplib.SMTP('smtp.office365.com', 587)
server.starttls()
server.login("", "")


model_cfg = os.path.join('.', 'model', 'cfg', 'conf.cfg')
model_weights = os.path.join('.', 'model', 'weights', 'model.weights')
class_names = os.path.join('.', 'model', 'names', 'class.names')


input_dir = 'data'

for img_name in os.listdir(input_dir):

    img_path = os.path.join(input_dir, img_name)

    with open(class_names, 'r') as f:
        class_names = [j[:-1] for j in f.readlines() if len(j) > 2]
        f.close()

    net = cv2.dnn.readNetFromDarknet(model_cfg, model_weights)


    img = cv2.imread(img_path)

    H, W, _ = img.shape

    blob = cv2.dnn.blobFromImage(img, 1 / 255, (416, 416), (0, 0, 0), True)

    net.setInput(blob)

    detections = util.get_outputs(net)

    bboxes = []
    class_ids = []
    scores = []

    for detection in detections:
        bbox = detection[:4]

        xc, yc, w, h = bbox
        bbox = [int(xc * W), int(yc * H), int(w * W), int(h * H)]

        bbox_confidence = detection[4]

        class_id = np.argmax(detection[5:])
        score = np.amax(detection[5:])

        bboxes.append(bbox)
        class_ids.append(class_id)
        scores.append(score)

    bboxes, class_ids, scores = util.NMS(bboxes, class_ids, scores)

    reader = easyocr.Reader(['en'], gpu=True)
    for bbox_, bbox in enumerate(bboxes):
        xc, yc, w, h = bbox

        license_plate = img[int(yc - (h / 2)):int(yc + (h / 2)), int(xc - (w / 2)):int(xc + (w / 2)), :].copy()

        img = cv2.rectangle(img,
                            (int(xc - (w / 2)), int(yc - (h / 2))),
                            (int(xc + (w / 2)), int(yc + (h / 2))),
                            (0, 255, 0),
                            15)

        license_plate_gray = cv2.cvtColor(license_plate, cv2.COLOR_BGR2GRAY)

        _, license_plate_thresh = cv2.threshold(license_plate_gray, 64, 255, cv2.THRESH_BINARY_INV)

        output = reader.readtext(license_plate_thresh)

        for out in output:
            text_bbox, text, text_score = out
            if text_score > 0.4:
                print(text, text_score)

                mycursor = mydb.cursor()

                mycursor.execute("SELECT * FROM masini_furate")

                myresult = mycursor.fetchall()

                ok_furat = 0

                for x in myresult:
                    if text == x[0] and text_score > float(x[1]):
                        print("MASINA FURATA! ", text)
                        ok_furat = 1
                        g = geocoder.ip('me')
                        sql = "UPDATE masini_furate SET latitudine=%s,longitudine=%s,zi=%s WHERE nume_placuta=%s"
                        val = (g.latlng[0], g.latlng[1], datetime.now().strftime("%d/%m/%Y %H:%M:%S"), text)
                        mycursor.execute(sql, val)
                        print("COORDONATELE AU FOST ACTUALIZATE")
                        mydb.commit()

                        map_url = "https://www.google.com/maps/place/{},{}".format(g.latlng[0], g.latlng[1])

                        msg = MIMEText("Masina furata la latitudinea " + str(g.latlng[0]) + "si longitudinea " + str(
                            g.latlng[1]) + "\n" + "Iată locația ta pe Google Maps: {}".format(map_url))

                        msg['From'] = "cristi.comunicat2023@outlook.com"
                        msg['To'] = "miloiuc4@gmail.com"
                        msg['Subject'] = "MASINA FURATA " + text

                        server.sendmail("cristi.comunicat2023@outlook.com", "miloiuc4@gmail.com", msg.as_string())

                        break

                if ok_furat == 0:
                    print("MASINA NU A FOST FURATA! ", text)

                mycursor_parcari = mydb.cursor()

                mycursor_parcari.execute("SELECT * FROM usertable")

                myresult_parcari = mycursor_parcari.fetchall()

                ok_parcari = 0

                for x in myresult_parcari:
                    if text == x[7] :

                        print("Masina se afla in baza de date a parcarii:", text)
                        print(x[0], " ",text)
                        ok_parcari = 1
                        today = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                        data_str = x[3]
                        data_str = data_str.strip()

                        data_str2 = x[2]
                        data_str2 = data_str2.strip()
                        data_str3 = today
                        data_str3 = data_str3.strip()

                        dif1 = datetime.strptime(data_str, '%d/%m/%Y %H:%M:%S')

                        dif3 = datetime.strptime(data_str3, '%d/%m/%Y %H:%M:%S')

                        dif2 = datetime.strptime(data_str2, '%H:%M:%S')

                        if (dif1 - dif3).total_seconds():
                            msg = MIMEText(
                                "Masina dumneavoastra a stat in parcare mai mult decat ar fi trebuit, ati intrat la " +
                                x[3] + " si ati iesit la " + today + "\n" + "Ar fi trebuit sa stati " + x[
                                    2] + "\n" + " aveti de platit 2lei ")

                            msg['From'] = "cristi.comunicat2023@outlook.com"
                            msg['To'] = str(x[4])
                            msg['Subject'] = "MASINA FURATA " + text

                            server.sendmail("cristi.comunicat2023@outlook.com", str(x[4]), msg.as_string())

                        break

                if ok_parcari == 0:
                    print("Masina nu se afla in baza de date a parcarii: ", text)
                    print(x[7], " ", text)

                mycursor_scan = mydb.cursor()

                mycursor_scan.execute("SELECT * FROM masini_scanate")

                myresult_scan = mycursor_scan.fetchall()
                ok_scanat = 0
                for x in myresult_scan:

                    if text == x[0] and text_score > float(x[1]):
                        ok_scanat = 1
                        print("Masina a fost scanata deja ", text)

                if ok_scanat == 0:
                    g = geocoder.ip('me')
                    sql = "INSERT INTO masini_scanate (nume_placuta,scor,latitudine,longitudine,data) VALUES(%s,%s,%s,%s,%s)"
                    val = (text, float("{:.1f}".format(text_score)) - 0.1, g.latlng[0], g.latlng[1],
                           datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                    mycursor_scan.execute(sql, val)
                    mydb.commit()
                    print("Scanare cu succes!")

    plt.figure()
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    plt.figure()
    plt.imshow(cv2.cvtColor(license_plate, cv2.COLOR_BGR2RGB))

    plt.figure()
    plt.imshow(cv2.cvtColor(license_plate_gray, cv2.COLOR_BGR2RGB))

    plt.figure()
    plt.imshow(cv2.cvtColor(license_plate_thresh, cv2.COLOR_BGR2RGB))

    plt.show()