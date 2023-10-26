INSERT INTO semester(name, student_pay, graduate_pay, budget)
VALUES
    ("אביב 2024", 12.5, 18.75, 100000),
    ("קיץ 2024", 12.7, 19, 100000);

INSERT INTO user(id, password, name, mail, role, is_student)
VALUES
    (111111111, 'scrypt:32768:8:1$9JlLLORwqo0Z8lx5$bf30bd33933489d768e99036386cd541de9083b3e2c7076121d86d8d64a9c61a62328ae63f9e6794d4d5957ada26899297759be682c8410980c00155eb2ee078', --321123
    'Bob Ross', 'bob@ros.com', 1, 0),
    (222222222, 'scrypt:32768:8:1$euCiJJBV41Iu6mIs$3228d730dcad2704b3485359db4de899b901d663f1fa9d490b13ce9ce36c3a90a05efb3d586548373ed30c52bd64ec047b8c13cc8824c0fa106d04b234b21d46', --password
    'Michael Jordan', 'michael.jordan@gmail.com', 2, 1),
    (333333333, 'scrypt:32768:8:1$MQb8PSufDZe2RAkb$ac2f5e8e192203e8b5b296fa7b1571fccf8c52f10576766946ba94809589ff0a7b685b628631417c9efd5b9b9ef872d597118f7d91d1ce55a5aefc0633ea6530', --secret
    'Noa Meir', 'noa.meir.noa@ynet.co.il', 2, 0);