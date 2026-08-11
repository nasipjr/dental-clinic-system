-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: dental_clinic
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `appointment`
--

DROP TABLE IF EXISTS `appointment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appointment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `appointment_date` datetime NOT NULL,
  `reason` varchar(255) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `session_opened_at` datetime DEFAULT NULL,
  `doctor_id` int DEFAULT NULL,
  `duration` int NOT NULL DEFAULT '30',
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  KEY `doctor_id` (`doctor_id`),
  CONSTRAINT `appointment_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE,
  CONSTRAINT `appointment_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1232 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appointment`
--

LOCK TABLES `appointment` WRITE;
/*!40000 ALTER TABLE `appointment` DISABLE KEYS */;
INSERT INTO `appointment` VALUES (1231,208,'2026-08-12 02:20:25',NULL,'Scheduled',NULL,NULL,30);
/*!40000 ALTER TABLE `appointment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `expense`
--

DROP TABLE IF EXISTS `expense`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `expense` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category` varchar(100) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `expense_date` date NOT NULL,
  `notes` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expense`
--

LOCK TABLES `expense` WRITE;
/*!40000 ALTER TABLE `expense` DISABLE KEYS */;
/*!40000 ALTER TABLE `expense` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `installment`
--

DROP TABLE IF EXISTS `installment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `installment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `treatment_plan_id` int NOT NULL,
  `amount` float NOT NULL,
  `due_date` date NOT NULL,
  `status` varchar(50) NOT NULL,
  `payment_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `treatment_plan_id` (`treatment_plan_id`),
  KEY `payment_id` (`payment_id`),
  CONSTRAINT `installment_ibfk_1` FOREIGN KEY (`treatment_plan_id`) REFERENCES `treatment_plan` (`id`) ON DELETE CASCADE,
  CONSTRAINT `installment_ibfk_2` FOREIGN KEY (`payment_id`) REFERENCES `payment` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `installment`
--

LOCK TABLES `installment` WRITE;
/*!40000 ALTER TABLE `installment` DISABLE KEYS */;
/*!40000 ALTER TABLE `installment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoice`
--

DROP TABLE IF EXISTS `invoice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice` (
  `id` int NOT NULL AUTO_INCREMENT,
  `appointment_id` int NOT NULL,
  `patient_id` int NOT NULL,
  `issue_date` datetime NOT NULL,
  `discount` decimal(10,2) NOT NULL,
  `discount_type` varchar(20) NOT NULL,
  `additional_charges` decimal(10,2) NOT NULL,
  `tax_rate` decimal(5,2) NOT NULL,
  `notes` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `appointment_id` (`appointment_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `invoice_ibfk_1` FOREIGN KEY (`appointment_id`) REFERENCES `appointment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `invoice_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=887 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice`
--

LOCK TABLES `invoice` WRITE;
/*!40000 ALTER TABLE `invoice` DISABLE KEYS */;
/*!40000 ALTER TABLE `invoice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification_log`
--

DROP TABLE IF EXISTS `notification_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notification_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `appointment_id` int NOT NULL,
  `patient_id` int NOT NULL,
  `type` varchar(50) NOT NULL,
  `channel` varchar(20) NOT NULL,
  `recipient` varchar(100) NOT NULL,
  `sent_at` datetime NOT NULL,
  `status` varchar(20) NOT NULL,
  `error_message` text,
  PRIMARY KEY (`id`),
  KEY `appointment_id` (`appointment_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `notification_log_ibfk_1` FOREIGN KEY (`appointment_id`) REFERENCES `appointment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `notification_log_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification_log`
--

LOCK TABLES `notification_log` WRITE;
/*!40000 ALTER TABLE `notification_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `notification_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patient`
--

DROP TABLE IF EXISTS `patient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patient` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(20) DEFAULT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `preferred_first_name` varchar(100) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `gender` varchar(20) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `post_code` varchar(20) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `notes` text,
  `medical_information` text,
  `appointment_notes` text,
  `occupation` varchar(150) DEFAULT NULL,
  `emergency_contact` varchar(150) DEFAULT NULL,
  `medicare_number` varchar(100) DEFAULT NULL,
  `telegram_chat_id` varchar(50) DEFAULT NULL,
  `reminders_enabled` tinyint(1) NOT NULL,
  `primary_doctor_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_patient_primary_doctor` (`primary_doctor_id`),
  CONSTRAINT `fk_patient_primary_doctor` FOREIGN KEY (`primary_doctor_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=209 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient`
--

LOCK TABLES `patient` WRITE;
/*!40000 ALTER TABLE `patient` DISABLE KEYS */;
INSERT INTO `patient` VALUES (208,NULL,'Test','Patient',NULL,NULL,NULL,'0500000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL);
/*!40000 ALTER TABLE `patient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patient_file`
--

DROP TABLE IF EXISTS `patient_file`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patient_file` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `filename` varchar(255) NOT NULL,
  `filepath` varchar(255) NOT NULL,
  `filetype` varchar(100) DEFAULT NULL,
  `upload_date` datetime NOT NULL,
  `notes` text,
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `patient_file_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient_file`
--

LOCK TABLES `patient_file` WRITE;
/*!40000 ALTER TABLE `patient_file` DISABLE KEYS */;
/*!40000 ALTER TABLE `patient_file` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_date` datetime NOT NULL,
  `notes` text,
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=756 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_allocation`
--

DROP TABLE IF EXISTS `payment_allocation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_allocation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `payment_id` int NOT NULL,
  `invoice_id` int NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `payment_id` (`payment_id`),
  KEY `invoice_id` (`invoice_id`),
  CONSTRAINT `payment_allocation_ibfk_1` FOREIGN KEY (`payment_id`) REFERENCES `payment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `payment_allocation_ibfk_2` FOREIGN KEY (`invoice_id`) REFERENCES `invoice` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=904 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_allocation`
--

LOCK TABLES `payment_allocation` WRITE;
/*!40000 ALTER TABLE `payment_allocation` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment_allocation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `staff_salary`
--

DROP TABLE IF EXISTS `staff_salary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staff_salary` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `salary_type` varchar(20) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `deduction_day` int NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `notes` text,
  `last_deducted_month` varchar(7) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `staff_salary_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staff_salary`
--

LOCK TABLES `staff_salary` WRITE;
/*!40000 ALTER TABLE `staff_salary` DISABLE KEYS */;
/*!40000 ALTER TABLE `staff_salary` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_setting`
--

DROP TABLE IF EXISTS `system_setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_setting` (
  `id` int NOT NULL AUTO_INCREMENT,
  `key` varchar(100) NOT NULL,
  `value` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_system_setting_key` (`key`)
) ENGINE=InnoDB AUTO_INCREMENT=248 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_setting`
--

LOCK TABLES `system_setting` WRITE;
/*!40000 ALTER TABLE `system_setting` DISABLE KEYS */;
INSERT INTO `system_setting` VALUES (189,'clinic_name','Clinic'),(190,'clinic_phone','+963 958 948 727'),(191,'clinic_email','kh.nasipdragon@gmail.com'),(192,'clinic_address','Damascus, Syria'),(193,'developer_whatsapp','963958948727'),(194,'currency_symbol','$'),(195,'default_appointment_duration','30'),(196,'auto_cancel_expired_minutes','120'),(197,'auto_close_open_session_minutes','120'),(198,'working_hours_start','09:00'),(199,'working_hours_end','19:00'),(200,'working_days','0,1,2,3,4,5,6'),(201,'treatment_prices','{\"\\u0641\\u062d\\u0635 \\u062f\\u0648\\u0631\\u064a \\u0648\\u0627\\u0633\\u062a\\u0634\\u0627\\u0631\\u0629\": 25000, \"\\u0635\\u0648\\u0631\\u0629 \\u0628\\u0627\\u0646\\u0648\\u0631\\u0627\\u0645\\u064a\\u0629 \\u0644\\u0644\\u0623\\u0633\\u0646\\u0627\\u0646\": 50000, \"\\u0623\\u0634\\u0639\\u0629 \\u0633\\u064a\\u0646\\u064a\\u0629 (\\u0634\\u0639\\u0627\\u0639\\u064a\\u0629)\": 20000, \"\\u0643\\u0634\\u0641 \\u0623\\u0644\\u0645 \\u0637\\u0627\\u0631\\u0626\": 60000, \"\\u0645\\u062a\\u0627\\u0628\\u0639\\u0629 \\u062f\\u0648\\u0631\\u064a\\u0629\": 20000, \"\\u062d\\u0634\\u0648\\u0629 \\u0636\\u0648\\u0626\\u064a\\u0629 \\u0643\\u0648\\u0645\\u0628\\u0648\\u0632\\u064a\\u062a\": 60000, \"\\u062a\\u0646\\u0638\\u064a\\u0641 \\u0648\\u062a\\u0644\\u0645\\u064a\\u0639 \\u0627\\u0644\\u0623\\u0633\\u0646\\u0627\\u0646 \\u0648\\u062a\\u0642\\u0644\\u064a\\u062d\": 50000, \"\\u062d\\u0634\\u0648\\u0629 \\u062a\\u062c\\u0645\\u064a\\u0644\\u064a\\u0629\": 200000, \"\\u062d\\u0634\\u0648\\u0629 \\u0636\\u0648\\u0626\\u064a\\u0629 \\u0643\\u0648\\u0645\\u0628\\u0648\\u0632\\u064a\\u062a (\\u0633\\u0637\\u062d \\u0648\\u0627\\u062d\\u062f)\": 60000, \"\\u062d\\u0634\\u0648\\u0629 \\u0636\\u0648\\u0626\\u064a\\u0629 \\u0643\\u0648\\u0645\\u0628\\u0648\\u0632\\u064a\\u062a (\\u0639\\u062f\\u0629 \\u0633\\u0637\\u0648\\u062d)\": 85000, \"\\u062d\\u0634\\u0648\\u0629 \\u0623\\u0645\\u0644\\u063a\\u0645 \\u0645\\u0644\\u063a\\u0645\\u064a\\u0629\": 55000, \"\\u062a\\u0628\\u064a\\u064a\\u0636 \\u0627\\u0644\\u0623\\u0633\\u0646\\u0627\\u0646 \\u0628\\u0627\\u0644\\u0644\\u064a\\u0632\\u0631/\\u0627\\u0644\\u0636\\u0648\\u0621\": 120000, \"\\u0639\\u062f\\u0633\\u0627\\u062a \\u0641\\u064a\\u0646\\u064a\\u0631 \\u062a\\u062c\\u0645\\u064a\\u0644\\u064a\\u0629\": 250000, \"\\u062c\\u0644\\u0633\\u0629 \\u0633\\u062d\\u0628 \\u0639\\u0635\\u0628 \\u0648\\u062a\\u0646\\u0638\\u064a\\u0641 \\u0642\\u0646\\u0648\\u0627\\u062a\": 200000, \"\\u062d\\u0634\\u0648 \\u0642\\u0646\\u0648\\u0627\\u062a \\u0648\\u062d\\u0634\\u0648 \\u0646\\u0647\\u0627\\u0626\\u064a (\\u0639\\u0635\\u0628)\": 150000, \"\\u0625\\u0639\\u0627\\u062f\\u0629 \\u0639\\u0644\\u0627\\u062c \\u0639\\u0635\\u0628 \\u0633\\u0627\\u0628\\u0642\": 180000, \"\\u0648\\u062a\\u062f \\u0641\\u0627\\u064a\\u0628\\u0631 \\u0645\\u0639 \\u062d\\u0634\\u0648\\u0629 \\u0628\\u0646\\u0627\\u0621\": 100000, \"\\u0642\\u0644\\u0639 \\u0633\\u0646 \\u0639\\u0627\\u062f\\u064a\": 80000, \"\\u0645\\u0639\\u0627\\u0644\\u062c\\u0629 \\u0645\\u0627 \\u0628\\u0639\\u062f \\u0627\\u0644\\u0642\\u0644\\u0639\": 30000, \"\\u0642\\u0644\\u0639 \\u062c\\u0631\\u0627\\u062d\\u064a / \\u0636\\u0631\\u0633 \\u0639\\u0642\\u0644 \\u0627\\u0646\\u062d\\u0634\\u0627\\u0631\\u064a\": 180000, \"\\u0632\\u0631\\u0639 \\u0633\\u0646 (\\u0632\\u0631\\u0639\\u0629 \\u062a\\u064a\\u062a\\u0627\\u0646\\u064a\\u0648\\u0645)\": 450000, \"\\u0637\\u0639\\u0648\\u0645 \\u0639\\u0638\\u0645\\u064a\\u0629 \\u0648\\u0631\\u0641\\u0639 \\u062c\\u064a\\u0628 \\u0641\\u0643\\u064a\": 350000, \"\\u062a\\u0627\\u062c \\u0632\\u064a\\u0631\\u0643\\u0648\\u0646 / \\u0628\\u0648\\u0631\\u0633\\u0644\\u064a\\u0646\": 200000, \"\\u062c\\u0633\\u0631 \\u0623\\u0633\\u0646\\u0627\\u0646 \\u062b\\u0627\\u0628\\u062a\": 350000, \"\\u062a\\u0627\\u062c \\u0625\\u064a\\u0645\\u0627\\u0643\\u0633 \\u062a\\u062c\\u0645\\u064a\\u0644\\u064a\": 230000, \"\\u0637\\u0642\\u0645 \\u0623\\u0633\\u0646\\u0627\\u0646 \\u0645\\u062a\\u062d\\u0631\\u0643 \\u0643\\u0627\\u0645\\u0644\\u0627\\u064b\": 350000, \"\\u0637\\u0642\\u0645 \\u0623\\u0633\\u0646\\u0627\\u0646 \\u062c\\u0632\\u0626\\u064a \\u0647\\u064a\\u0643\\u0644\\u064a\": 250000, \"\\u0637\\u0628\\u0639\\u0629 \\u0623\\u0633\\u0646\\u0627\\u0646 \\u0648\\u062a\\u0623\\u0637\\u064a\\u0631\": 40000, \"\\u062a\\u0631\\u0643\\u064a\\u0628 \\u062a\\u0642\\u0648\\u064a\\u0645 \\u0623\\u0633\\u0646\\u0627\\u0646\": 600000, \"\\u062c\\u0644\\u0633\\u0629 \\u0634\\u062f \\u0648\\u062a\\u0641\\u0642\\u062f \\u062a\\u0642\\u0648\\u064a\\u0645\": 35000, \"\\u0641\\u0643 \\u062a\\u0642\\u0648\\u064a\\u0645 \\u0648\\u062a\\u062b\\u0628\\u064a\\u062a\": 120000, \"\\u062a\\u0642\\u0648\\u064a\\u0645 \\u0634\\u0641\\u0627\\u0641 (\\u0635\\u064a\\u0646\\u064a\\u0629)\": 750000, \"\\u062d\\u0634\\u0648\\u0629 \\u0623\\u0637\\u0641\\u0627\\u0644 \\u0645\\u062e\\u0635\\u0635\\u0629\": 45000, \"\\u0628\\u062a\\u0631 \\u0639\\u0635\\u0628 \\u0623\\u0637\\u0641\\u0627\\u0644 (\\u0633\\u062d\\u0628 \\u0639\\u0635\\u0628 \\u0644\\u0628\\u0628\\u064a)\": 70000, \"\\u062d\\u0627\\u0641\\u0638 \\u0645\\u0633\\u0627\\u0641\\u0629 \\u0644\\u0644\\u0623\\u0637\\u0641\\u0627\\u0644\": 80000, \"\\u062a\\u063a\\u0644\\u064a\\u0641 \\u0645\\u064a\\u0627\\u0632\\u064a\\u0628 \\u0648\\u0642\\u0627\\u0626\\u064a\": 35000, \"\\u062a\\u0637\\u0628\\u064a\\u0642 \\u0641\\u0644\\u0648\\u0631\\u0627\\u064a\\u062f \\u0648\\u0642\\u0627\\u0626\\u064a\": 30000, \"\\u0645\\u0639\\u0627\\u0644\\u062c\\u0629 \\u062d\\u0633\\u0627\\u0633\\u064a\\u0627\\u062a \\u0627\\u0644\\u0623\\u0633\\u0646\\u0627\\u0646\": 35000, \"\\u0648\\u0627\\u0642\\u064a \\u0644\\u064a\\u0644\\u064a \\u0636\\u062f \\u0627\\u0644\\u0635\\u0631\\u064a\\u0631\": 100000, \"\\u0639\\u0644\\u0627\\u062c \\u0627\\u0644\\u062a\\u0647\\u0627\\u0628\\u0627\\u062a \\u0627\\u0644\\u0644\\u062b\\u0629\": 60000, \"\\u0634\\u0647\\u0627\\u062f\\u0629 \\u062a\\u0642\\u0631\\u064a\\u0631 \\u0637\\u0628\\u064a\": 25000}'),(202,'anesthesia_needle_price','50000'),(203,'notification_enable_sms','false'),(204,'notification_enable_telegram','false'),(205,'notification_enable_email','false'),(206,'telegram_bot_token',''),(207,'telegram_24h_enabled','true'),(208,'telegram_2h_enabled','true'),(209,'telegram_24h_template','تذكير موعد من {clinic_name}: مرحباً {patient_name}، نود تذكيركم بموعدكم غداً بتاريخ {appointment_time}. نتمنى لكم السلامة.'),(210,'telegram_2h_template','تذكير موعد من {clinic_name}: مرحباً {patient_name}، نود تذكيركم بموعدكم اليوم بعد ساعتين في تمام الساعة {appointment_time}. بانتظاركم.'),(211,'commpeak_api_key',''),(212,'commpeak_stream_id',''),(213,'smtp_host','smtp.gmail.com'),(214,'smtp_port','587'),(215,'smtp_user',''),(216,'smtp_password',''),(217,'smtp_from_email',''),(218,'email_24h_enabled','true'),(219,'email_2h_enabled','true'),(220,'email_24h_subject','تذكير بموعدك لدى {clinic_name}'),(221,'email_24h_template','عزيزي {patient_name}،\n\nهذا تذكير بموعدك لدى {clinic_name} غداً بتاريخ {appointment_time}.\n\nنتمنى لكم السلامة.\n\nمع تحيات،\n{clinic_name}'),(222,'email_2h_subject','تذكير بموعدك لدى {clinic_name}'),(223,'email_2h_template','عزيزي {patient_name}،\n\nهذا تذكير بموعدك لدى {clinic_name} اليوم بعد ساعتين في تمام الساعة {appointment_time}.\n\nبانتظاركم.\n\nمع تحيات،\n{clinic_name}'),(224,'sms_24h_enabled','true'),(225,'sms_2h_enabled','true'),(226,'sms_24h_template','تذكير من {clinic_name}: موعدك بتاريخ {appointment_time}. يرجى الحضور في الوقت المحدد.'),(227,'sms_2h_template','تذكير من {clinic_name}: موعدك بتاريخ {appointment_time}. يرجى الحضور في الوقت المحدد.'),(228,'sms_cancel_enabled','true'),(229,'sms_reschedule_enabled','true'),(230,'telegram_cancel_enabled','true'),(231,'telegram_reschedule_enabled','true'),(232,'email_cancel_enabled','true'),(233,'email_reschedule_enabled','true'),(234,'sms_cancel_template','تنبيه من {clinic_name}: تم إلغاء موعدك المحدد بتاريخ {appointment_time}.'),(235,'sms_reschedule_template','تنبيه من {clinic_name}: تم تعديل موعدك ليصبح بتاريخ {appointment_time}. يرجى الحضور في الوقت المحدد.'),(236,'telegram_cancel_template','تنبيه من {clinic_name}: تم إلغاء موعدك المحدد بتاريخ {appointment_time}. نتمنى لكم السلامة.'),(237,'telegram_reschedule_template','تنبيه من {clinic_name}: تم تعديل موعدك ليصبح بتاريخ {appointment_time}. يرجى الحضور في الوقت المحدد.'),(238,'email_cancel_subject','إلغاء الموعد - {clinic_name}'),(239,'email_cancel_template','عزيزي {patient_name}،\n\nنود إعلامكم بأنه تم إلغاء موعدكم المحدد بتاريخ {appointment_time}.\n\nنتمنى لكم السلامة.\n\nمع تحيات،\n{clinic_name}'),(240,'email_reschedule_subject','تعديل موعدك لدى {clinic_name}'),(241,'email_reschedule_template','عزيزي {patient_name}،\n\nنود إعلامكم بأنه تم تعديل موعدكم ليصبح بتاريخ {appointment_time}.\n\nيرجى الحضور في الوقت المحدد.\n\nمع تحيات،\n{clinic_name}'),(242,'tax_rate','15'),(243,'clinic_vat_number',''),(244,'booking_window_days','60'),(245,'active_license_key','DCMS-T15-20260827-D38B646D89'),(246,'auto_trial_created_at','2026-08-12 02:20:24'),(247,'last_system_activity','2026-08-12 02:20:25');
/*!40000 ALTER TABLE `system_setting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tooth_history`
--

DROP TABLE IF EXISTS `tooth_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tooth_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `tooth_number` varchar(50) NOT NULL,
  `procedure_type` varchar(200) NOT NULL,
  `notes` text,
  `created_at` datetime DEFAULT NULL,
  `history_date` date DEFAULT NULL,
  `appointment_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `tooth_history_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=254 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tooth_history`
--

LOCK TABLES `tooth_history` WRITE;
/*!40000 ALTER TABLE `tooth_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `tooth_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `treatment`
--

DROP TABLE IF EXISTS `treatment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `treatment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `appointment_id` int NOT NULL,
  `treatment_date` datetime NOT NULL,
  `procedure_type` varchar(200) DEFAULT NULL,
  `tooth_number` varchar(50) DEFAULT NULL,
  `notes` text,
  `total_cost` decimal(10,2) DEFAULT NULL,
  `use_anesthesia` tinyint(1) NOT NULL,
  `anesthesia_needles` int NOT NULL,
  `anesthesia_cost` decimal(10,2) NOT NULL,
  `doctor_id` int DEFAULT NULL,
  `teeth_range` varchar(100) DEFAULT NULL,
  `quadrant` varchar(50) DEFAULT NULL,
  `jaw` varchar(50) DEFAULT NULL,
  `salary_expense_id` int DEFAULT NULL,
  `anesthesia_type` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `appointment_id` (`appointment_id`),
  KEY `doctor_id` (`doctor_id`),
  CONSTRAINT `treatment_ibfk_1` FOREIGN KEY (`appointment_id`) REFERENCES `appointment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `treatment_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1163 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `treatment`
--

LOCK TABLES `treatment` WRITE;
/*!40000 ALTER TABLE `treatment` DISABLE KEYS */;
/*!40000 ALTER TABLE `treatment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `treatment_plan`
--

DROP TABLE IF EXISTS `treatment_plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `treatment_plan` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `title` varchar(150) NOT NULL,
  `total_cost` float NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `treatment_plan_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `treatment_plan`
--

LOCK TABLES `treatment_plan` WRITE;
/*!40000 ALTER TABLE `treatment_plan` DISABLE KEYS */;
/*!40000 ALTER TABLE `treatment_plan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `patient_id` int DEFAULT NULL,
  `plain_password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_user_username` (`username`),
  KEY `fk_user_patient` (`patient_id`),
  CONSTRAINT `fk_user_patient` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'mazen','scrypt:32768:8:1$xhKFPs9qe3Y1EtWJ$2ef49bf9592168cb6cabd8b805dab4d97d6319265da2c959bb8a5c4bedede53ca5f4b1d598ae685ec8674873f2d39dd8b9b33d45848c83108d7db22a55c4b738','admin','Mazen','Admin',NULL,NULL),(10,'admin','scrypt:32768:8:1$14VK6uLVZSTQQWIj$082cebff6b887a4e9882e44c4e94d751ce2c364fa27cb029ff878c0250b8449974e95b9154e3dc035ff9a20fd92381c5adfec313450b7964a91049fbe77d199b','admin','المدير','العام',NULL,NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-12  2:21:07
