DROP DATABASE IF EXISTS `diabetic`;
CREATE DATABASE `diabetic`;
USE `diabetic`;

CREATE TABLE `users` (
    `id` INT PRIMARY KEY AUTO_INCREMENT, 
    `name` VARCHAR(1000),
    `email` VARCHAR(1000),
    `password` VARCHAR(225)
);


CREATE TABLE `predictions` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `user_name` VARCHAR(1000),
    `user_email` VARCHAR(1000),
    `image` VARCHAR(10000),
    `prediction` VARCHAR(225),
    `date` DATE,
    `time` TIME
);

