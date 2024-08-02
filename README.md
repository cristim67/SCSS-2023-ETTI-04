Second Place - Scientific Communication Session

This is an application that uses a YOLOv3 neural network to detect and recognize license plates from a set of images. To achieve this, the code loads the YOLOv3 model, defines directories for the configuration files and class lists, loads each image file from the specified directory, and applies the neural network to detect license plates. After detection, the license plates are extracted, converted to black-and-white images, and scanned using the EasyOCR library to recognize the characters on the license plates.

If there is a match with a license plate of a car reported as stolen in a MySQL database, the application will send an email to a specified address and update the geographical coordinates of the car in the database. Otherwise, the application will continue to run and proceed to detect license plates in the next image from the specified directory.

To accomplish this, the code also uses the Geocoder library to obtain the geographical coordinates of the user running the application and the SMTPlib library to send the email to the specified address.
