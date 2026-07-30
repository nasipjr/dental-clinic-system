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
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  KEY `doctor_id` (`doctor_id`),
  CONSTRAINT `appointment_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE,
  CONSTRAINT `appointment_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appointment`
--

LOCK TABLES `appointment` WRITE;
/*!40000 ALTER TABLE `appointment` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `appointment_id` (`appointment_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `invoice_ibfk_1` FOREIGN KEY (`appointment_id`) REFERENCES `appointment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `invoice_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient`
--

LOCK TABLES `patient` WRITE;
/*!40000 ALTER TABLE `patient` DISABLE KEYS */;
INSERT INTO `patient` VALUES (1,'mr','نسيب','جبارة',NULL,'2002-06-10','Male','+963958948727','kh.nasipdragon@gmail.com','اللاذقية استراد الزراعة','اللاذقية',NULL,NULL,'سوريا','لا','لا',NULL,'مهندس',NULL,NULL,'932284186',1,NULL),(2,'ms','جنا','عديرة',NULL,'2004-02-21','Female','+963938589133','janaodera0934099489@gmail.com','اللاذقية عين ام ابراهيم','اللاذقية',NULL,NULL,'سوريا','لا','لا',NULL,'صيدلانية','نسيب جبارة (+963958948727)',NULL,'5428455321',1,NULL);
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_allocation`
--

LOCK TABLES `payment_allocation` WRITE;
/*!40000 ALTER TABLE `payment_allocation` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment_allocation` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_setting`
--

LOCK TABLES `system_setting` WRITE;
/*!40000 ALTER TABLE `system_setting` DISABLE KEYS */;
INSERT INTO `system_setting` VALUES (1,'clinic_name','Dr Mazen Alshab'),(2,'clinic_phone','+963 991 142 959'),(3,'clinic_email','ma.mazen.alshab@gmail.com'),(4,'clinic_address','اللاذقية, الدعتور'),(5,'currency_symbol','SP'),(6,'default_appointment_duration','15'),(7,'working_hours_start','00:00'),(8,'working_hours_end','23:00'),(9,'working_days','0,1,2,3,4,5,6'),(10,'treatment_prices','{\"\\u0641\\u062d\\u0635 \\u062f\\u0648\\u0631\\u064a\": 25000, \"\\u062a\\u0646\\u0638\\u064a\\u0641 \\u0648\\u062a\\u0644\\u0645\\u064a\\u0639\": 50000, \"\\u062d\\u0634\\u0648\\u0629 \\u0623\\u0633\\u0646\\u0627\\u0646\": 75000, \"\\u0639\\u0644\\u0627\\u062c \\u0639\\u0635\\u0628 \\u0627\\u0644\\u0633\\u0646\": 150000, \"\\u062a\\u0627\\u062c / \\u062c\\u0633\\u0631\": 200000, \"\\u062a\\u0642\\u0648\\u064a\\u0645 \\u0627\\u0644\\u0623\\u0633\\u0646\\u0627\\u0646\": 300000, \"\\u062a\\u0628\\u064a\\u064a\\u0636 \\u0627\\u0644\\u0623\\u0633\\u0646\\u0627\\u0646\": 120000, \"\\u0623\\u0644\\u0645 \\u0637\\u0627\\u0631\\u0626\": 60000, \"\\u0642\\u0644\\u0639 \\u0633\\u0646\": 800000, \"\\u0645\\u0639\\u0627\\u0644\\u062c\\u0629 \\u0645\\u0627 \\u0628\\u0639\\u062f \\u0627\\u0644\\u0642\\u0644\\u0639\": 30000, \"\\u0632\\u064a\\u0631\\u0643\\u0648\\u0646 \\u0644\\u064a\\u0632\\u0631\\u064a\": 400000}'),(11,'notification_enable_sms','true'),(12,'notification_enable_whatsapp','false'),(13,'notification_enable_email','true'),(14,'twilio_account_sid',''),(15,'twilio_auth_token',''),(16,'twilio_phone_number',''),(17,'twilio_whatsapp_number',''),(18,'smtp_host','smtp.gmail.com'),(19,'smtp_port','587'),(20,'smtp_user','kh.nasipdragon@gmail.com'),(21,'smtp_password','gela rjdv ynqx ijto'),(22,'smtp_from_email','kh.nasipdragon@gmail.com'),(23,'tax_rate','15'),(24,'clinic_vat_number',''),(25,'booking_window_days','35'),(26,'notification_enable_telegram','true'),(27,'telegram_bot_token','8732677418:AAGqRTIJyPDl4-mbTGEuoGLcsgF3yUlGha4'),(28,'easysendsms_username','nasikh.nqcg3d2026'),(29,'easysendsms_password','nj0958948727nj'),(30,'easysendsms_sender','DrClinic'),(31,'commpeak_api_key','65959128dc1fd202542a36cc65600c98032826248369a6cb733fc628eee278a336b54f5929ad7bb56aae82f0d600afe0e975fe8ea8'),(32,'commpeak_stream_id',''),(33,'telegram_24h_enabled','true'),(34,'telegram_2h_enabled','true'),(35,'telegram_24h_template','تذكير موعد من {clinic_name}: مرحباً {المريض_name}، نود تذكيركم بموعدكم غداً بتاريخ {الموعد_الوقت}. نتمنى لكم السلامة.'),(36,'telegram_2h_template','تذكير موعد من {clinic_name}: مرحباً {المريض_name}، نود تذكيركم بموعدكم اليوم بعد ساعتين في تمام الساعة {الموعد_الوقت}. بانتظاركم.'),(37,'email_24h_enabled','true'),(38,'email_2h_enabled','true'),(39,'email_24h_subject','تذكير بموعدك لدى {clinic_name}'),(40,'email_24h_template','عزيزي {المريض_name}،\r\n\r\nهذا تذكير بموعدك لدى {clinic_name} غداً بتاريخ {الموعد_الوقت}.\r\n\r\nنتمنى لكم السلامة.\r\n\r\nمع تحيات،\r\n{clinic_name}'),(41,'email_2h_subject','تذكير بموعدك لدى {clinic_name}'),(42,'email_2h_template','عزيزي {المريض_name}،\r\n\r\nهذا تذكير بموعدك لدى {clinic_name} اليوم بعد ساعتين في تمام الساعة {الموعد_الوقت}.\r\n\r\nبانتظاركم.\r\n\r\nمع تحيات،\r\n{clinic_name}'),(43,'sms_cancel_enabled','true'),(44,'sms_reschedule_enabled','true'),(45,'telegram_cancel_enabled','true'),(46,'telegram_reschedule_enabled','true'),(47,'email_cancel_enabled','true'),(48,'email_reschedule_enabled','true'),(49,'sms_cancel_template','تنبيه من {clinic_name}: تم إلغاء موعدك المحدد بتاريخ {الموعد_الوقت}.'),(50,'sms_reschedule_template','تنبيه من {clinic_name}: تم تعديل موعدك ليصبح بتاريخ {الموعد_الوقت}. يرجى الحضور في الوقت المحدد.'),(51,'telegram_cancel_template','تنبيه من {clinic_name}: تم إلغاء موعدك المحدد بتاريخ {الموعد_الوقت}. نتمنى لكم السلامة.'),(52,'telegram_reschedule_template','تنبيه من {clinic_name}: تم تعديل موعدك ليصبح بتاريخ {الموعد_الوقت}. يرجى الحضور في الوقت المحدد.'),(53,'email_cancel_subject','إلغاء الموعد - {clinic_name}'),(54,'email_cancel_template','عزيزي {المريض_name}، نود إعلامكم بأنه تم إلغاء موعدكم المحدد بتاريخ {الموعد_الوقت}. نتمنى لكم السلامة. مع تحيات، {clinic_name}'),(55,'email_reschedule_subject','تعديل موعدك لدى {clinic_name}'),(56,'email_reschedule_template','عزيزي {المريض_name}، نود إعلامكم بأنه تم تعديل موعدكم ليصبح بتاريخ {الموعد_الوقت}. يرجى الحضور في الوقت المحدد. مع تحيات، {clinic_name}'),(57,'sms_24h_enabled','true'),(58,'sms_2h_enabled','true'),(59,'sms_24h_template','تذكير من {clinic_name}: موعدك بتاريخ {الموعد_الوقت}. يرجى الحضور في الوقت المحدد.'),(60,'sms_2h_template','تذكير من {clinic_name}: موعدك بتاريخ {الموعد_الوقت}. يرجى الحضور في الوقت المحدد.'),(61,'anesthesia_needle_price','50000'),(62,'active_license_key','DCMS-LIFE-21260629-08B67A0754'),(63,'license_type','lifetime'),(64,'license_expires_at','2126-06-29 23:59:59'),(65,'last_system_activity','2026-07-30 17:53:29'),(66,'developer_whatsapp','963958948727'),(67,'auto_cancel_expired_minutes','0');
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
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `tooth_history_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
  PRIMARY KEY (`id`),
  KEY `appointment_id` (`appointment_id`),
  KEY `doctor_id` (`doctor_id`),
  CONSTRAINT `treatment_ibfk_1` FOREIGN KEY (`appointment_id`) REFERENCES `appointment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `treatment_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'mazen','scrypt:32768:8:1$oNovSpzMH22825Gx$44f0c43936738d6892f5ed7e0713a1052ffd37cb22f7af6984eb35c4717e3f1927caa905d50eb78d2d4b51878fd47e1b8f5ea898f6574b1e7ae56caf2c092095','admin','الدكتور','مازن',NULL,NULL),(2,'رند','scrypt:32768:8:1$2ShEFynmMI74D0ah$d8b6fee88bc07d4439c73ee0e2296ff7bf185f85c932470f35201a5c1ce3c118c13a5bb092c9fcf9f85803b0404fe0e8a4db827490e1a53a34dbcb86317e5932','receptionist','رند','سالم',NULL,NULL),(3,'nasip','scrypt:32768:8:1$LH7hoFjGYqxxjzHz$35065ea2b62df4a4aa0fc6b4e0388fa87acf770ad6adde0ed341c850f291008fa0ab1f775fce2ae5c1bd721cb3cd976cdaad6733b27b4a94ecd3ae444d08e5fd','patient','نسيب','جبارة',1,'nasip123'),(4,'jana','scrypt:32768:8:1$7PTKu4JOX6jvrNLV$0444c87daa1f5d9ddace0c494f5758b810bfce068091ad7f2c0685ef6dd75f6dc720262aded7f99cb5d7b1f2010b74342d5ad81ac4da4acbb0d416e4a2143072','patient','جنا','عديرة',2,'jana123');
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

-- Dump completed on 2026-07-30 17:53:36
