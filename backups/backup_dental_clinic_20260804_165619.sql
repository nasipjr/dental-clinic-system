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
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appointment`
--

LOCK TABLES `appointment` WRITE;
/*!40000 ALTER TABLE `appointment` DISABLE KEYS */;
INSERT INTO `appointment` VALUES (1,1,'2026-06-14 15:30:16','قلع سن','Cancelled',NULL,1),(2,1,'2026-07-07 16:45:16','تنظيف وتلميع','Done','2026-07-07 16:45:16',1),(3,2,'2026-06-19 13:00:16','حشوة أسنان','Done','2026-06-19 13:00:16',1),(4,3,'2026-06-06 16:00:16','تبييض الأسنان','Done','2026-06-06 16:00:16',1),(5,3,'2026-06-12 15:00:16','تنظيف وتلميع','Cancelled',NULL,1),(6,4,'2026-06-21 13:45:16','علاج عصب السن','Done','2026-06-21 13:45:16',1),(7,4,'2026-07-08 15:45:16','ألم طارئ','Done','2026-07-08 15:45:16',1),(8,4,'2026-06-10 13:15:16','تبييض الأسنان','Done','2026-06-10 13:15:16',1),(9,4,'2026-07-21 14:30:16','تاج / جسر','Done','2026-07-21 14:30:16',1),(10,5,'2026-06-27 17:00:16','تاج / جسر','Done','2026-06-27 17:00:16',1),(11,5,'2026-06-21 12:45:16','علاج عصب السن','Done','2026-06-21 12:45:16',1),(12,5,'2026-07-07 13:45:16','تاج / جسر','Done','2026-07-07 13:45:16',1),(13,6,'2026-06-28 16:45:16','قلع سن','Done','2026-06-28 16:45:16',1),(14,6,'2026-06-06 13:15:16','حشوة أسنان','Done','2026-06-06 13:15:16',1),(15,6,'2026-06-07 14:00:16','ألم طارئ','Cancelled',NULL,1),(16,7,'2026-07-11 16:00:16','تبييض الأسنان','Done','2026-07-11 16:00:16',1),(17,8,'2026-07-25 11:30:16','ألم طارئ','Done','2026-07-25 11:30:16',1),(18,8,'2026-07-02 12:45:16','تنظيف وتلميع','Done','2026-07-02 12:45:16',1),(19,9,'2026-06-20 11:45:16','قلع سن','Done','2026-06-20 11:45:16',1),(20,9,'2026-06-05 14:45:16','تبييض الأسنان','Done','2026-06-05 14:45:16',1),(21,9,'2026-07-21 10:30:16','تاج / جسر','Done','2026-07-21 10:30:16',1),(22,9,'2026-07-07 14:00:16','علاج عصب السن','Cancelled',NULL,1),(23,10,'2026-07-23 10:45:16','حشوة أسنان','Done','2026-07-23 10:45:16',1),(24,11,'2026-06-04 15:15:16','تاج / جسر','Done','2026-06-04 15:15:16',1),(25,11,'2026-06-23 17:15:16','ألم طارئ','Done','2026-06-23 17:15:16',1),(26,11,'2026-07-14 17:30:16','تنظيف وتلميع','Done','2026-07-14 17:30:16',1),(27,11,'2026-07-17 17:45:16','تاج / جسر','Done','2026-07-17 17:45:16',1),(28,12,'2026-06-23 11:45:16','ألم طارئ','Done','2026-06-23 11:45:16',1),(29,12,'2026-07-09 12:30:16','قلع سن','Done','2026-07-09 12:30:16',1),(30,13,'2026-07-22 15:30:16','علاج عصب السن','Cancelled',NULL,1),(31,14,'2026-07-25 12:45:16','تبييض الأسنان','Done','2026-07-25 12:45:16',1),(32,15,'2026-06-11 12:45:16','تبييض الأسنان','Cancelled',NULL,1),(33,15,'2026-07-11 15:45:16','ألم طارئ','Done','2026-07-11 15:45:16',1),(34,15,'2026-06-11 10:00:16','علاج عصب السن','Done','2026-06-11 10:00:16',1),(35,15,'2026-06-19 13:45:16','تاج / جسر','Cancelled',NULL,1),(36,16,'2026-06-25 12:30:16','تبييض الأسنان','Done','2026-06-25 12:30:16',1),(37,16,'2026-07-05 11:00:16','تبييض الأسنان','Cancelled',NULL,1),(38,16,'2026-07-20 17:00:16','ألم طارئ','Done','2026-07-20 17:00:16',1),(39,17,'2026-07-17 13:45:16','حشوة أسنان','Done','2026-07-17 13:45:16',1),(40,17,'2026-06-21 09:30:16','علاج عصب السن','Done','2026-06-21 09:30:16',1),(41,17,'2026-06-12 14:00:16','علاج عصب السن','Done','2026-06-12 14:00:16',1),(42,18,'2026-07-01 16:15:16','ألم طارئ','Done','2026-07-01 16:15:16',1),(43,19,'2026-06-27 14:30:16','تاج / جسر','Done','2026-06-27 14:30:16',1),(44,19,'2026-07-28 10:45:16','تبييض الأسنان','Done','2026-07-28 10:45:16',1),(45,20,'2026-07-24 16:00:16','ألم طارئ','Cancelled',NULL,1),(46,20,'2026-07-13 09:30:16','تبييض الأسنان','Done','2026-07-13 09:30:16',1),(47,20,'2026-06-18 13:00:16','تنظيف وتلميع','Done','2026-06-18 13:00:16',1),(48,21,'2026-06-17 16:00:16','قلع سن','Done','2026-06-17 16:00:16',1),(49,21,'2026-07-05 15:15:16','تبييض الأسنان','Done','2026-07-05 15:15:16',1),(50,21,'2026-06-06 13:15:16','قلع سن','Done','2026-06-06 13:15:16',1),(51,22,'2026-06-24 09:45:16','تنظيف وتلميع','Done','2026-06-24 09:45:16',1),(52,22,'2026-07-28 17:15:16','تنظيف وتلميع','Done','2026-07-28 17:15:16',1),(53,22,'2026-06-18 16:15:16','علاج عصب السن','Done','2026-06-18 16:15:16',1),(54,1,'2026-08-26 11:30:16','قلع سن','Scheduled',NULL,1),(55,2,'2026-08-07 16:00:16','قلع سن','Scheduled',NULL,1),(56,3,'2026-08-28 15:30:16','قلع سن','Scheduled','2026-07-30 18:11:20',1),(57,4,'2026-08-23 12:30:16','تاج / جسر','Scheduled',NULL,1),(58,5,'2026-08-24 15:00:16','تبييض الأسنان','Scheduled',NULL,1),(59,6,'2026-08-19 12:30:16','تنظيف وتلميع','Scheduled',NULL,1),(60,7,'2026-08-26 13:00:16','قلع سن','Scheduled','2026-07-30 18:11:47',1),(61,8,'2026-08-19 12:30:16','علاج عصب السن','Scheduled',NULL,1),(62,9,'2026-08-11 15:30:16','تبييض الأسنان','Scheduled',NULL,1),(63,10,'2026-08-07 09:00:16','علاج عصب السن','Scheduled','2026-07-30 18:11:03',1),(64,11,'2026-08-10 15:00:16','تبييض الأسنان','Scheduled',NULL,1),(65,12,'2026-08-07 10:00:16','قلع سن','Scheduled',NULL,1),(66,1,'2026-07-31 22:30:00','ألم طارئ','Cancelled',NULL,1),(67,1,'2026-08-11 03:30:00','تبييض الأسنان','Cancelled',NULL,1),(70,1,'2026-08-05 10:00:00','فحص دوري','Scheduled',NULL,1),(71,17,'2026-08-01 19:00:00','قلع سن','Cancelled',NULL,5),(72,13,'2026-08-01 21:30:00','ألم طارئ','Cancelled',NULL,1);
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expense`
--

LOCK TABLES `expense` WRITE;
/*!40000 ALTER TABLE `expense` DISABLE KEYS */;
INSERT INTO `expense` VALUES (1,'Rent',3000000.00,'2026-08-01','الايجار الشهري');
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
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice`
--

LOCK TABLES `invoice` WRITE;
/*!40000 ALTER TABLE `invoice` DISABLE KEYS */;
INSERT INTO `invoice` VALUES (1,2,1,'2026-07-07 16:45:16',0.00,'value',0.00,0.00),(2,3,2,'2026-06-19 13:00:16',0.00,'value',0.00,0.00),(3,4,3,'2026-06-06 16:00:16',10000.00,'value',0.00,0.00),(4,6,4,'2026-06-21 13:45:16',25000.00,'value',0.00,0.00),(5,7,4,'2026-07-08 15:45:16',0.00,'value',0.00,0.00),(6,8,4,'2026-06-10 13:15:16',0.00,'value',0.00,0.00),(7,9,4,'2026-07-21 14:30:16',0.00,'value',0.00,0.00),(8,10,5,'2026-06-27 17:00:16',0.00,'value',0.00,0.00),(9,11,5,'2026-06-21 12:45:16',0.00,'value',0.00,0.00),(10,12,5,'2026-07-07 13:45:16',0.00,'value',0.00,0.00),(11,13,6,'2026-06-28 16:45:16',0.00,'value',0.00,0.00),(12,14,6,'2026-06-06 13:15:16',0.00,'value',0.00,0.00),(13,16,7,'2026-07-11 16:00:16',0.00,'value',0.00,0.00),(14,17,8,'2026-07-25 11:30:16',0.00,'value',0.00,0.00),(15,18,8,'2026-07-02 12:45:16',0.00,'value',0.00,0.00),(16,19,9,'2026-06-20 11:45:16',0.00,'value',0.00,0.00),(17,20,9,'2026-06-05 14:45:16',0.00,'value',0.00,0.00),(18,21,9,'2026-07-21 10:30:16',0.00,'value',0.00,0.00),(19,23,10,'2026-07-23 10:45:16',0.00,'value',0.00,0.00),(20,24,11,'2026-06-04 15:15:16',0.00,'value',0.00,0.00),(21,25,11,'2026-06-23 17:15:16',0.00,'value',0.00,0.00),(22,26,11,'2026-07-14 17:30:16',0.00,'value',0.00,0.00),(23,27,11,'2026-07-17 17:45:16',20000.00,'value',0.00,0.00),(24,28,12,'2026-06-23 11:45:16',0.00,'value',0.00,0.00),(25,29,12,'2026-07-09 12:30:16',0.00,'value',0.00,0.00),(26,31,14,'2026-07-25 12:45:16',10000.00,'value',0.00,0.00),(27,33,15,'2026-07-11 15:45:16',0.00,'value',0.00,0.00),(28,34,15,'2026-06-11 10:00:16',0.00,'value',0.00,0.00),(29,36,16,'2026-06-25 12:30:16',0.00,'value',0.00,0.00),(30,38,16,'2026-07-20 17:00:16',0.00,'value',0.00,0.00),(31,39,17,'2026-07-17 13:45:16',0.00,'value',0.00,0.00),(32,40,17,'2026-06-21 09:30:16',20000.00,'value',0.00,0.00),(33,41,17,'2026-06-12 14:00:16',20000.00,'value',0.00,0.00),(34,42,18,'2026-07-01 16:15:16',0.00,'value',0.00,0.00),(35,43,19,'2026-06-27 14:30:16',0.00,'value',0.00,0.00),(36,44,19,'2026-07-28 10:45:16',10000.00,'value',0.00,0.00),(37,46,20,'2026-07-13 09:30:16',0.00,'value',0.00,0.00),(38,47,20,'2026-06-18 13:00:16',10000.00,'value',0.00,0.00),(39,48,21,'2026-06-17 16:00:16',25000.00,'value',0.00,0.00),(40,49,21,'2026-07-05 15:15:16',0.00,'value',0.00,0.00),(41,50,21,'2026-06-06 13:15:16',10000.00,'value',0.00,0.00),(42,51,22,'2026-06-24 09:45:16',0.00,'value',0.00,0.00),(43,52,22,'2026-07-28 17:15:16',0.00,'value',0.00,0.00),(44,53,22,'2026-06-18 16:15:16',0.00,'value',0.00,0.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification_log`
--

LOCK TABLES `notification_log` WRITE;
/*!40000 ALTER TABLE `notification_log` DISABLE KEYS */;
INSERT INTO `notification_log` VALUES (1,67,1,'sms_cancel','sms','+963958948727','2026-07-31 21:39:04','failed','API Error 401: {\"status\":false,\"error_code\":\"0x13\",\"message\":\"Not authenticated - invalid token for this origin\"}'),(2,67,1,'telegram_cancel','telegram','932284186','2026-07-31 21:39:06','sent',NULL),(3,67,1,'email_cancel','email','kh.nasipdragon@gmail.com','2026-07-31 21:39:21','failed','timed out'),(4,72,13,'sms_2h','sms','+96394094628','2026-08-01 18:43:39','failed','API Error 401: {\"status\":false,\"error_code\":\"0x13\",\"message\":\"Not authenticated - invalid token for this origin\"}'),(5,72,13,'email_2h','email','patient11@clinic.com','2026-08-01 18:43:55','failed','timed out'),(6,72,13,'sms_reschedule','sms','+96394094628','2026-08-01 18:49:06','failed','API Error 401: {\"status\":false,\"error_code\":\"0x13\",\"message\":\"Not authenticated - invalid token for this origin\"}');
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
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient`
--

LOCK TABLES `patient` WRITE;
/*!40000 ALTER TABLE `patient` DISABLE KEYS */;
INSERT INTO `patient` VALUES (1,'mr','نسيب','جبارة',NULL,'2002-06-10','Male','+963958948727','kh.nasipdragon@gmail.com','اللاذقية استراد الزراعة','اللاذقية',NULL,NULL,'سوريا','لا','لا',NULL,'مهندس',NULL,NULL,'932284186',1,NULL),(2,'ms','جنا','عديرة',NULL,'2004-02-21','Female','+963938589133','janaodera0934099489@gmail.com','اللاذقية عين ام ابراهيم','اللاذقية',NULL,NULL,'سوريا','لا','لا',NULL,'صيدلانية','نسيب جبارة (+963958948727)',NULL,'5428455321',1,NULL),(3,'السيد','أحمد','العلي',NULL,'1970-12-05','Male','+96398055317','patient1@clinic.com','حي المالكي','دمشق',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','نزف لثة خفيف عند التفريش',NULL,NULL,NULL,NULL,NULL,1,NULL),(4,'الآنسة/السيدة','فاطمة','الحمصي',NULL,'1992-04-16','Female','+96391944434','patient2@clinic.com','حي المالكي','حماة',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','لا توجد أمراض مزمنة',NULL,NULL,NULL,NULL,NULL,1,NULL),(5,'الآنسة/السيدة','مريم','الشامي',NULL,'1998-03-08','Female','+96397252144','patient3@clinic.com','حي المالكي','اللاذقية',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','حساسية للبنسلين',NULL,NULL,NULL,NULL,NULL,1,NULL),(6,'الآنسة/السيدة','ريم','البغدادي',NULL,'1995-06-22','Female','+96398081625','patient4@clinic.com','حي الفرقان','طرطوس',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','لا توجد حساسية معروفة',NULL,NULL,NULL,NULL,NULL,1,NULL),(7,'السيد','طارق','الخطيب',NULL,'1986-06-11','Male','+96391126604','patient5@clinic.com','حي الميدان','حلب',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','حساسية للبنسلين',NULL,NULL,NULL,NULL,NULL,1,NULL),(8,'الآنسة/السيدة','هدى','الحلبي',NULL,'1966-10-28','Female','+96396152837','patient6@clinic.com','حي الميدان','حمص',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','سكري من النوع الثاني',NULL,NULL,NULL,NULL,NULL,1,NULL),(9,'السيد','عبد الرحمن','الأحمد',NULL,'1975-10-07','Male','+96395284081','patient7@clinic.com','حي الفرقان','اللاذقية',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','حساسية للبنسلين',NULL,NULL,NULL,NULL,NULL,1,NULL),(10,'الآنسة/السيدة','رانيا','الأتاسي',NULL,'1990-07-18','Female','+96391951113','patient8@clinic.com','حي الميدان','اللاذقية',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','لا توجد حساسية معروفة',NULL,NULL,NULL,NULL,NULL,1,NULL),(11,'الآنسة/السيدة','أمل','الجابري',NULL,'1977-07-25','Female','+96394758488','patient9@clinic.com','حي الفرقان','اللاذقية',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','ارتفاع ضغط الدم - يتناول أدوية منظمة',NULL,NULL,NULL,NULL,NULL,1,NULL),(12,'الآنسة/السيدة','سلمى','قدور',NULL,'1972-04-22','Female','+96397607440','patient10@clinic.com','حي المزة','دمشق',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','سكري من النوع الثاني',NULL,NULL,NULL,NULL,NULL,1,NULL),(13,'الآنسة/السيدة','سارة','الكردي',NULL,'2007-01-22','Female','+96394094628','patient11@clinic.com','حي الزهراء','حلب',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','سكري من النوع الثاني',NULL,NULL,NULL,NULL,NULL,1,NULL),(14,'السيد','محمد','الصالح',NULL,'2006-10-17','Male','+96399884094','patient12@clinic.com','حي الفرقان','حمص',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','لا توجد أمراض مزمنة',NULL,NULL,NULL,NULL,NULL,1,NULL),(15,'الآنسة/السيدة','مريم','النابلسي',NULL,'1968-08-13','Female','+96396986361','patient13@clinic.com','حي المزة','طرطوس',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','لا توجد أمراض مزمنة',NULL,NULL,NULL,NULL,NULL,1,NULL),(16,'الآنسة/السيدة','ريم','الحكيم',NULL,'1988-04-22','Female','+96396773384','patient14@clinic.com','حي الفرقان','اللاذقية',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','ارتفاع ضغط الدم - يتناول أدوية منظمة',NULL,NULL,NULL,NULL,NULL,1,NULL),(17,'السيد','طارق','درويش',NULL,'1991-11-07','Male','+96394098035','patient15@clinic.com','حي الزهراء','دمشق',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','حساسية للبنسلين',NULL,NULL,NULL,NULL,NULL,1,NULL),(18,'الآنسة/السيدة','هدى','الساعدي',NULL,'1968-09-27','Female','+96393460821','patient16@clinic.com','حي المزة','اللاذقية',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','ارتفاع ضغط الدم - يتناول أدوية منظمة',NULL,NULL,NULL,NULL,NULL,1,NULL),(19,'الآنسة/السيدة','نور الهدى','المرادي',NULL,'1992-08-09','Female','+96399173109','patient17@clinic.com','حي المزة','حماة',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','ارتفاع ضغط الدم - يتناول أدوية منظمة',NULL,NULL,NULL,NULL,NULL,1,NULL),(20,'السيد','حمزة','زريق',NULL,'2004-04-14','Male','+96395010541','patient18@clinic.com','حي المالكي','اللاذقية',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','لا توجد أمراض مزمنة',NULL,NULL,NULL,NULL,NULL,1,NULL),(21,'السيد','بلال','الخوري',NULL,'2002-11-14','Male','+96393471744','patient19@clinic.com','حي الروضة','حلب',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','حساسية للبنسلين',NULL,NULL,NULL,NULL,NULL,1,NULL),(22,'السيد','زياد','الجراح',NULL,'1985-10-09','Male','+96394235763','patient20@clinic.com','حي الميدان','حلب',NULL,NULL,NULL,'مريض جديد تم إضافته تلقائياً للاختبار','لا توجد أمراض مزمنة',NULL,NULL,NULL,NULL,NULL,1,NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
INSERT INTO `payment` VALUES (1,1,125000.00,'2026-07-07 17:30:16','سداد دفعة نقدية بالاستقبال'),(2,2,525000.00,'2026-06-19 13:45:16','سداد دفعة نقدية بالاستقبال'),(3,3,95000.00,'2026-06-06 16:45:16','سداد دفعة نقدية بالاستقبال'),(4,4,110000.00,'2026-06-21 14:30:16','سداد دفعة نقدية بالاستقبال'),(5,4,100000.00,'2026-07-08 16:30:16','سداد دفعة نقدية بالاستقبال'),(6,4,200000.00,'2026-06-10 14:00:16','سداد دفعة نقدية بالاستقبال'),(7,4,225000.00,'2026-07-21 15:15:16','سداد دفعة نقدية بالاستقبال'),(8,5,575000.00,'2026-06-27 17:45:16','سداد دفعة نقدية بالاستقبال'),(9,5,125000.00,'2026-06-21 13:30:16','سداد دفعة نقدية بالاستقبال'),(10,5,250000.00,'2026-07-07 14:30:16','سداد دفعة نقدية بالاستقبال'),(11,6,625000.00,'2026-06-28 17:30:16','سداد دفعة نقدية بالاستقبال'),(12,6,25000.00,'2026-06-06 14:00:16','سداد دفعة نقدية بالاستقبال'),(13,7,600000.00,'2026-07-11 16:45:16','سداد دفعة نقدية بالاستقبال'),(14,8,255000.00,'2026-07-25 12:15:16','سداد دفعة نقدية بالاستقبال'),(15,8,120000.00,'2026-07-02 13:30:16','سداد دفعة نقدية بالاستقبال'),(16,9,750000.00,'2026-06-20 12:30:16','سداد دفعة نقدية بالاستقبال'),(17,9,400000.00,'2026-06-05 15:30:16','سداد دفعة نقدية بالاستقبال'),(18,9,500000.00,'2026-07-21 11:15:16','سداد دفعة نقدية بالاستقبال'),(19,10,70000.00,'2026-07-23 11:30:16','سداد دفعة نقدية بالاستقبال'),(20,11,840000.00,'2026-06-04 16:00:16','سداد دفعة نقدية بالاستقبال'),(21,11,450000.00,'2026-06-23 18:00:16','سداد دفعة نقدية بالاستقبال'),(22,11,250000.00,'2026-07-14 18:15:16','سداد دفعة نقدية بالاستقبال'),(23,11,110000.00,'2026-07-17 18:30:16','سداد دفعة نقدية بالاستقبال'),(24,12,100000.00,'2026-06-23 12:30:16','سداد دفعة نقدية بالاستقبال'),(25,12,350000.00,'2026-07-09 13:15:16','سداد دفعة نقدية بالاستقبال'),(26,14,170000.00,'2026-07-25 13:30:16','سداد دفعة نقدية بالاستقبال'),(27,15,150000.00,'2026-07-11 16:30:16','سداد دفعة نقدية بالاستقبال'),(28,15,455000.00,'2026-06-11 10:45:16','سداد دفعة نقدية بالاستقبال'),(29,16,350000.00,'2026-06-25 13:15:16','سداد دفعة نقدية بالاستقبال'),(30,16,80000.00,'2026-07-20 17:45:16','سداد دفعة نقدية بالاستقبال'),(31,17,125000.00,'2026-07-17 14:30:16','سداد دفعة نقدية بالاستقبال'),(32,17,305000.00,'2026-06-21 10:15:16','سداد دفعة نقدية بالاستقبال'),(33,17,735000.00,'2026-06-12 14:45:16','سداد دفعة نقدية بالاستقبال'),(34,18,1125000.00,'2026-07-01 17:00:16','سداد دفعة نقدية بالاستقبال'),(35,19,170000.00,'2026-06-27 15:15:16','سداد دفعة نقدية بالاستقبال'),(36,19,40000.00,'2026-07-28 11:30:16','سداد دفعة نقدية بالاستقبال'),(37,20,320000.00,'2026-07-13 10:15:16','سداد دفعة نقدية بالاستقبال'),(38,20,545000.00,'2026-06-18 13:45:16','سداد دفعة نقدية بالاستقبال'),(39,21,175000.00,'2026-06-17 16:45:16','سداد دفعة نقدية بالاستقبال'),(40,21,162500.00,'2026-07-05 16:00:16','سداد دفعة نقدية بالاستقبال'),(41,21,470000.00,'2026-06-06 14:00:16','سداد دفعة نقدية بالاستقبال'),(42,22,155000.00,'2026-06-24 10:30:16','سداد دفعة نقدية بالاستقبال'),(43,22,450000.00,'2026-07-28 18:00:16','سداد دفعة نقدية بالاستقبال'),(44,22,125000.00,'2026-06-18 17:00:16','سداد دفعة نقدية بالاستقبال');
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
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_allocation`
--

LOCK TABLES `payment_allocation` WRITE;
/*!40000 ALTER TABLE `payment_allocation` DISABLE KEYS */;
INSERT INTO `payment_allocation` VALUES (1,1,1,125000.00),(2,2,2,425000.00),(3,3,3,95000.00),(4,4,4,110000.00),(5,5,5,100000.00),(6,6,6,200000.00),(7,7,7,225000.00),(8,8,8,475000.00),(9,9,9,125000.00),(10,10,10,250000.00),(11,11,11,625000.00),(12,12,12,25000.00),(13,13,13,550000.00),(14,14,14,205000.00),(15,15,15,120000.00),(16,16,16,700000.00),(17,17,17,400000.00),(18,18,18,400000.00),(19,19,19,50000.00),(20,20,20,790000.00),(21,21,21,450000.00),(22,22,22,200000.00),(23,23,23,110000.00),(24,24,24,50000.00),(25,25,25,250000.00),(26,26,26,170000.00),(27,27,27,150000.00),(28,28,28,455000.00),(29,29,29,350000.00),(30,30,30,80000.00),(34,34,34,1125000.00),(35,35,35,170000.00),(36,36,36,40000.00),(37,37,37,320000.00),(38,38,38,545000.00),(39,39,39,175000.00),(40,40,40,162500.00),(41,41,41,470000.00),(42,42,42,155000.00),(43,43,43,450000.00),(44,44,44,125000.00),(48,33,33,735000.00),(49,32,32,305000.00),(50,31,31,125000.00);
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_setting`
--

LOCK TABLES `system_setting` WRITE;
/*!40000 ALTER TABLE `system_setting` DISABLE KEYS */;
INSERT INTO `system_setting` VALUES (1,'clinic_name','Dr Mazen Alshab'),(2,'clinic_phone','+963 991 142 959'),(3,'clinic_email','ma.mazen.alshab@gmail.com'),(4,'clinic_address','اللاذقية, الدعتور'),(5,'currency_symbol','SP'),(6,'default_appointment_duration','15'),(7,'working_hours_start','00:00'),(8,'working_hours_end','23:00'),(9,'working_days','0,1,2,3,4,5,6'),(10,'treatment_prices','{\"\\u0641\\u062d\\u0635 \\u062f\\u0648\\u0631\\u064a\": 25000, \"\\u062a\\u0646\\u0638\\u064a\\u0641 \\u0648\\u062a\\u0644\\u0645\\u064a\\u0639\": 50000, \"\\u062d\\u0634\\u0648\\u0629 \\u0623\\u0633\\u0646\\u0627\\u0646\": 75000, \"\\u0639\\u0644\\u0627\\u062c \\u0639\\u0635\\u0628 \\u0627\\u0644\\u0633\\u0646\": 150000, \"\\u062a\\u0627\\u062c / \\u062c\\u0633\\u0631\": 200000, \"\\u062a\\u0642\\u0648\\u064a\\u0645 \\u0627\\u0644\\u0623\\u0633\\u0646\\u0627\\u0646\": 300000, \"\\u062a\\u0628\\u064a\\u064a\\u0636 \\u0627\\u0644\\u0623\\u0633\\u0646\\u0627\\u0646\": 120000, \"\\u0623\\u0644\\u0645 \\u0637\\u0627\\u0631\\u0626\": 60000, \"\\u0642\\u0644\\u0639 \\u0633\\u0646\": 800000, \"\\u0645\\u0639\\u0627\\u0644\\u062c\\u0629 \\u0645\\u0627 \\u0628\\u0639\\u062f \\u0627\\u0644\\u0642\\u0644\\u0639\": 30000, \"\\u0632\\u064a\\u0631\\u0643\\u0648\\u0646 \\u0644\\u064a\\u0632\\u0631\\u064a\": 400000}'),(11,'notification_enable_sms','true'),(12,'notification_enable_whatsapp','false'),(13,'notification_enable_email','true'),(14,'twilio_account_sid',''),(15,'twilio_auth_token',''),(16,'twilio_phone_number',''),(17,'twilio_whatsapp_number',''),(18,'smtp_host','smtp.gmail.com'),(19,'smtp_port','587'),(20,'smtp_user','kh.nasipdragon@gmail.com'),(21,'smtp_password','gela rjdv ynqx ijto'),(22,'smtp_from_email','kh.nasipdragon@gmail.com'),(23,'tax_rate','15'),(24,'clinic_vat_number',''),(25,'booking_window_days','35'),(26,'notification_enable_telegram','true'),(27,'telegram_bot_token','8732677418:AAGqRTIJyPDl4-mbTGEuoGLcsgF3yUlGha4'),(28,'easysendsms_username','nasikh.nqcg3d2026'),(29,'easysendsms_password','nj0958948727nj'),(30,'easysendsms_sender','DrClinic'),(31,'commpeak_api_key','65959128dc1fd202542a36cc65600c98032826248369a6cb733fc628eee278a336b54f5929ad7bb56aae82f0d600afe0e975fe8ea8'),(32,'commpeak_stream_id',''),(33,'telegram_24h_enabled','true'),(34,'telegram_2h_enabled','true'),(35,'telegram_24h_template','تذكير موعد من {clinic_name}: مرحباً {المريض_name}، نود تذكيركم بموعدكم غداً بتاريخ {الموعد_الوقت}. نتمنى لكم السلامة.'),(36,'telegram_2h_template','تذكير موعد من {clinic_name}: مرحباً {المريض_name}، نود تذكيركم بموعدكم اليوم بعد ساعتين في تمام الساعة {الموعد_الوقت}. بانتظاركم.'),(37,'email_24h_enabled','true'),(38,'email_2h_enabled','true'),(39,'email_24h_subject','تذكير بموعدك لدى {clinic_name}'),(40,'email_24h_template','عزيزي {المريض_name}،\r\n\r\nهذا تذكير بموعدك لدى {clinic_name} غداً بتاريخ {الموعد_الوقت}.\r\n\r\nنتمنى لكم السلامة.\r\n\r\nمع تحيات،\r\n{clinic_name}'),(41,'email_2h_subject','تذكير بموعدك لدى {clinic_name}'),(42,'email_2h_template','عزيزي {المريض_name}،\r\n\r\nهذا تذكير بموعدك لدى {clinic_name} اليوم بعد ساعتين في تمام الساعة {الموعد_الوقت}.\r\n\r\nبانتظاركم.\r\n\r\nمع تحيات،\r\n{clinic_name}'),(43,'sms_cancel_enabled','true'),(44,'sms_reschedule_enabled','true'),(45,'telegram_cancel_enabled','true'),(46,'telegram_reschedule_enabled','true'),(47,'email_cancel_enabled','true'),(48,'email_reschedule_enabled','true'),(49,'sms_cancel_template','تنبيه من {clinic_name}: تم إلغاء موعدك المحدد بتاريخ {الموعد_الوقت}.'),(50,'sms_reschedule_template','تنبيه من {clinic_name}: تم تعديل موعدك ليصبح بتاريخ {الموعد_الوقت}. يرجى الحضور في الوقت المحدد.'),(51,'telegram_cancel_template','تنبيه من {clinic_name}: تم إلغاء موعدك المحدد بتاريخ {الموعد_الوقت}. نتمنى لكم السلامة.'),(52,'telegram_reschedule_template','تنبيه من {clinic_name}: تم تعديل موعدك ليصبح بتاريخ {الموعد_الوقت}. يرجى الحضور في الوقت المحدد.'),(53,'email_cancel_subject','إلغاء الموعد - {clinic_name}'),(54,'email_cancel_template','عزيزي {المريض_name}، نود إعلامكم بأنه تم إلغاء موعدكم المحدد بتاريخ {الموعد_الوقت}. نتمنى لكم السلامة. مع تحيات، {clinic_name}'),(55,'email_reschedule_subject','تعديل موعدك لدى {clinic_name}'),(56,'email_reschedule_template','عزيزي {المريض_name}، نود إعلامكم بأنه تم تعديل موعدكم ليصبح بتاريخ {الموعد_الوقت}. يرجى الحضور في الوقت المحدد. مع تحيات، {clinic_name}'),(57,'sms_24h_enabled','true'),(58,'sms_2h_enabled','true'),(59,'sms_24h_template','تذكير من {clinic_name}: موعدك بتاريخ {الموعد_الوقت}. يرجى الحضور في الوقت المحدد.'),(60,'sms_2h_template','تذكير من {clinic_name}: موعدك بتاريخ {الموعد_الوقت}. يرجى الحضور في الوقت المحدد.'),(61,'anesthesia_needle_price','50000'),(62,'active_license_key','DCMS-LIFE-21260629-08B67A0754'),(63,'license_type','lifetime'),(64,'license_expires_at','2126-06-29 23:59:59'),(65,'last_system_activity','2026-08-04 16:48:40'),(66,'developer_whatsapp','963958948727'),(67,'auto_cancel_expired_minutes','60');
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
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `tooth_history_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tooth_history`
--

LOCK TABLES `tooth_history` WRITE;
/*!40000 ALTER TABLE `tooth_history` DISABLE KEYS */;
INSERT INTO `tooth_history` VALUES (1,1,'17','فحص دوري','معالجة تاريخية للسن رقم 17','2026-07-07 16:45:16',NULL),(2,2,'25','فحص دوري','معالجة تاريخية للسن رقم 25','2026-06-19 13:00:16',NULL),(3,2,'45','تقويم الأسنان','معالجة تاريخية للسن رقم 45','2026-06-19 13:00:16',NULL),(4,3,'26','علاج عصب السن','معالجة تاريخية للسن رقم 26','2026-06-06 16:00:16',NULL),(5,4,'38','تبييض الأسنان','معالجة تاريخية للسن رقم 38','2026-06-21 13:45:16',NULL),(6,4,'43','فحص دوري','معالجة تاريخية للسن رقم 43','2026-06-21 13:45:16',NULL),(7,4,'12','تنظيف وتلميع','معالجة تاريخية للسن رقم 12','2026-07-08 15:45:16',NULL),(8,4,'15','علاج عصب السن','معالجة تاريخية للسن رقم 15','2026-06-10 13:15:16',NULL),(9,4,'43','تاج / جسر','معالجة تاريخية للسن رقم 43','2026-07-21 14:30:16',NULL),(10,4,'22','فحص دوري','معالجة تاريخية للسن رقم 22','2026-07-21 14:30:16',NULL),(11,5,'41','فحص دوري','معالجة تاريخية للسن رقم 41','2026-06-27 17:00:16',NULL),(12,5,'14','زيركون ليزري','معالجة تاريخية للسن رقم 14','2026-06-27 17:00:16',NULL),(13,5,'43','فحص دوري','معالجة تاريخية للسن رقم 43','2026-06-21 12:45:16',NULL),(14,5,'14','حشوة أسنان','معالجة تاريخية للسن رقم 14','2026-07-07 13:45:16',NULL),(15,5,'41','حشوة أسنان','معالجة تاريخية للسن رقم 41','2026-07-07 13:45:16',NULL),(16,6,'35','علاج عصب السن','معالجة تاريخية للسن رقم 35','2026-06-28 16:45:16',NULL),(17,6,'12','حشوة أسنان','معالجة تاريخية للسن رقم 12','2026-06-28 16:45:16',NULL),(18,6,'45','تقويم الأسنان','معالجة تاريخية للسن رقم 45','2026-06-28 16:45:16',NULL),(19,6,'38','تنظيف وتلميع','معالجة تاريخية للسن رقم 38','2026-06-06 13:15:16',NULL),(20,7,'37','علاج عصب السن','معالجة تاريخية للسن رقم 37','2026-07-11 16:00:16',NULL),(21,7,'34','تقويم الأسنان','معالجة تاريخية للسن رقم 34','2026-07-11 16:00:16',NULL),(22,8,'31','فحص دوري','معالجة تاريخية للسن رقم 31','2026-07-25 11:30:16',NULL),(23,8,'46','قلع سن','معالجة تاريخية للسن رقم 46','2026-07-25 11:30:16',NULL),(24,8,'41','تبييض الأسنان','معالجة تاريخية للسن رقم 41','2026-07-02 12:45:16',NULL),(25,9,'23','زيركون ليزري','معالجة تاريخية للسن رقم 23','2026-06-20 11:45:16',NULL),(26,9,'16','تاج / جسر','معالجة تاريخية للسن رقم 16','2026-06-20 11:45:16',NULL),(27,9,'17','زيركون ليزري','معالجة تاريخية للسن رقم 17','2026-06-05 14:45:16',NULL),(28,9,'14','فحص دوري','معالجة تاريخية للسن رقم 14','2026-07-21 10:30:16',NULL),(29,9,'13','فحص دوري','معالجة تاريخية للسن رقم 13','2026-07-21 10:30:16',NULL),(30,9,'24','علاج عصب السن','معالجة تاريخية للسن رقم 24','2026-07-21 10:30:16',NULL),(31,10,'31','تنظيف وتلميع','معالجة تاريخية للسن رقم 31','2026-07-23 10:45:16',NULL),(32,11,'34','تبييض الأسنان','معالجة تاريخية للسن رقم 34','2026-06-04 15:15:16',NULL),(33,11,'13','زيركون ليزري','معالجة تاريخية للسن رقم 13','2026-06-04 15:15:16',NULL),(34,11,'15','تبييض الأسنان','معالجة تاريخية للسن رقم 15','2026-06-04 15:15:16',NULL),(35,11,'36','تقويم الأسنان','معالجة تاريخية للسن رقم 36','2026-06-23 17:15:16',NULL),(36,11,'33','حشوة أسنان','معالجة تاريخية للسن رقم 33','2026-06-23 17:15:16',NULL),(37,11,'47','فحص دوري','معالجة تاريخية للسن رقم 47','2026-06-23 17:15:16',NULL),(38,11,'28','علاج عصب السن','معالجة تاريخية للسن رقم 28','2026-07-14 17:30:16',NULL),(39,11,'45','تبييض الأسنان','معالجة تاريخية للسن رقم 45','2026-07-17 17:45:16',NULL),(40,11,'16','تبييض الأسنان','معالجة تاريخية للسن رقم 16','2026-07-17 17:45:16',NULL),(41,12,'46','تنظيف وتلميع','معالجة تاريخية للسن رقم 46','2026-06-23 11:45:16',NULL),(42,12,'34','تبييض الأسنان','معالجة تاريخية للسن رقم 34','2026-07-09 12:30:16',NULL),(43,12,'11','تنظيف وتلميع','معالجة تاريخية للسن رقم 11','2026-07-09 12:30:16',NULL),(44,12,'33','قلع سن','معالجة تاريخية للسن رقم 33','2026-07-09 12:30:16',NULL),(45,14,'48','تقويم الأسنان','معالجة تاريخية للسن رقم 48','2026-07-25 12:45:16',NULL),(46,15,'23','تنظيف وتلميع','معالجة تاريخية للسن رقم 23','2026-07-11 15:45:16',NULL),(47,15,'23','فحص دوري','معالجة تاريخية للسن رقم 23','2026-06-11 10:00:16',NULL),(48,15,'34','قلع سن','معالجة تاريخية للسن رقم 34','2026-06-11 10:00:16',NULL),(49,15,'35','تاج / جسر','معالجة تاريخية للسن رقم 35','2026-06-11 10:00:16',NULL),(50,16,'25','تنظيف وتلميع','معالجة تاريخية للسن رقم 25','2026-06-25 12:30:16',NULL),(51,16,'46','تنظيف وتلميع','معالجة تاريخية للسن رقم 46','2026-06-25 12:30:16',NULL),(52,16,'15','علاج عصب السن','معالجة تاريخية للسن رقم 15','2026-06-25 12:30:16',NULL),(53,16,'18','قلع سن','معالجة تاريخية للسن رقم 18','2026-07-20 17:00:16',NULL),(54,17,'43','تنظيف وتلميع','معالجة تاريخية للسن رقم 43','2026-07-17 13:45:16',NULL),(55,17,'36','حشوة أسنان','معالجة تاريخية للسن رقم 36','2026-07-17 13:45:16',NULL),(56,17,'27','تاج / جسر','معالجة تاريخية للسن رقم 27','2026-06-21 09:30:16',NULL),(57,17,'23','حشوة أسنان','معالجة تاريخية للسن رقم 23','2026-06-21 09:30:16',NULL),(58,17,'47','قلع سن','معالجة تاريخية للسن رقم 47','2026-06-12 14:00:16',NULL),(59,17,'37','حشوة أسنان','معالجة تاريخية للسن رقم 37','2026-06-12 14:00:16',NULL),(60,17,'11','زيركون ليزري','معالجة تاريخية للسن رقم 11','2026-06-12 14:00:16',NULL),(61,18,'21','حشوة أسنان','معالجة تاريخية للسن رقم 21','2026-07-01 16:15:16',NULL),(62,18,'14','زيركون ليزري','معالجة تاريخية للسن رقم 14','2026-07-01 16:15:16',NULL),(63,18,'17','زيركون ليزري','معالجة تاريخية للسن رقم 17','2026-07-01 16:15:16',NULL),(64,19,'42','تبييض الأسنان','معالجة تاريخية للسن رقم 42','2026-06-27 14:30:16',NULL),(65,19,'45','تنظيف وتلميع','معالجة تاريخية للسن رقم 45','2026-07-28 10:45:16',NULL),(66,20,'34','علاج عصب السن','معالجة تاريخية للسن رقم 34','2026-07-13 09:30:16',NULL),(67,20,'18','تبييض الأسنان','معالجة تاريخية للسن رقم 18','2026-07-13 09:30:16',NULL),(68,20,'31','زيركون ليزري','معالجة تاريخية للسن رقم 31','2026-06-18 13:00:16',NULL),(69,20,'11','تقويم الأسنان','معالجة تاريخية للسن رقم 11','2026-06-18 13:00:16',NULL),(70,20,'45','تاج / جسر','معالجة تاريخية للسن رقم 45','2026-06-18 13:00:16',NULL),(71,21,'22','علاج عصب السن','معالجة تاريخية للسن رقم 22','2026-06-17 16:00:16',NULL),(72,21,'18','تنظيف وتلميع','معالجة تاريخية للسن رقم 18','2026-07-05 15:15:16',NULL),(73,21,'47','حشوة أسنان','معالجة تاريخية للسن رقم 47','2026-07-05 15:15:16',NULL),(74,21,'34','قلع سن','معالجة تاريخية للسن رقم 34','2026-06-06 13:15:16',NULL),(75,21,'16','قلع سن','معالجة تاريخية للسن رقم 16','2026-06-06 13:15:16',NULL),(76,21,'27','تبييض الأسنان','معالجة تاريخية للسن رقم 27','2026-06-06 13:15:16',NULL),(77,22,'44','قلع سن','معالجة تاريخية للسن رقم 44','2026-06-24 09:45:16',NULL),(78,22,'22','حشوة أسنان','معالجة تاريخية للسن رقم 22','2026-06-24 09:45:16',NULL),(79,22,'22','زيركون ليزري (سابق)','معالجة تاريخية للسن رقم 22','2026-07-28 17:15:16','2027-01-20'),(80,22,'16','فحص دوري','معالجة تاريخية للسن رقم 16','2026-06-18 16:15:16',NULL),(93,22,'22','تنظيف وتلميع (سابق)','2021','2026-08-03 21:35:46','2021-01-01'),(94,22,'16','ألم طارئ (سابق)','خراج','2026-08-03 21:44:34','2020-06-10');
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
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `treatment`
--

LOCK TABLES `treatment` WRITE;
/*!40000 ALTER TABLE `treatment` DISABLE KEYS */;
INSERT INTO `treatment` VALUES (1,2,'2026-07-07 16:45:16','فحص دوري','17','تم إنجاز فحص دوري بنجاح للسن رقم 17',125000.00,1,2,100000.00,NULL),(2,3,'2026-06-19 13:00:16','فحص دوري','25','تم إنجاز فحص دوري بنجاح للسن رقم 25',25000.00,0,0,0.00,NULL),(3,3,'2026-06-19 13:00:16','تقويم الأسنان','45','تم إنجاز تقويم الأسنان بنجاح للسن رقم 45',400000.00,1,2,100000.00,NULL),(4,4,'2026-06-06 16:00:16','علاج عصب السن','26','تم إنجاز علاج عصب السن بنجاح للسن رقم 26',200000.00,1,1,50000.00,NULL),(5,6,'2026-06-21 13:45:16','تبييض الأسنان','38','تم إنجاز تبييض الأسنان بنجاح للسن رقم 38',220000.00,1,2,100000.00,NULL),(6,6,'2026-06-21 13:45:16','فحص دوري','43','تم إنجاز فحص دوري بنجاح للسن رقم 43',25000.00,0,0,0.00,NULL),(7,7,'2026-07-08 15:45:16','تنظيف وتلميع','12','تم إنجاز تنظيف وتلميع بنجاح للسن رقم 12',100000.00,1,1,50000.00,NULL),(8,8,'2026-06-10 13:15:16','علاج عصب السن','15','تم إنجاز علاج عصب السن بنجاح للسن رقم 15',200000.00,1,1,50000.00,NULL),(9,9,'2026-07-21 14:30:16','تاج / جسر','43','تم إنجاز تاج / جسر بنجاح للسن رقم 43',200000.00,0,0,0.00,NULL),(10,9,'2026-07-21 14:30:16','فحص دوري','22','تم إنجاز فحص دوري بنجاح للسن رقم 22',25000.00,0,0,0.00,NULL),(11,10,'2026-06-27 17:00:16','فحص دوري','41','تم إنجاز فحص دوري بنجاح للسن رقم 41',25000.00,0,0,0.00,NULL),(12,10,'2026-06-27 17:00:16','زيركون ليزري','14','تم إنجاز زيركون ليزري بنجاح للسن رقم 14',450000.00,1,1,50000.00,NULL),(13,11,'2026-06-21 12:45:16','فحص دوري','43','تم إنجاز فحص دوري بنجاح للسن رقم 43',125000.00,1,2,100000.00,NULL),(14,12,'2026-07-07 13:45:16','حشوة أسنان','14','تم إنجاز حشوة أسنان بنجاح للسن رقم 14',175000.00,1,2,100000.00,NULL),(15,12,'2026-07-07 13:45:16','حشوة أسنان','41','تم إنجاز حشوة أسنان بنجاح للسن رقم 41',75000.00,0,0,0.00,NULL),(16,13,'2026-06-28 16:45:16','علاج عصب السن','35','تم إنجاز علاج عصب السن بنجاح للسن رقم 35',150000.00,0,0,0.00,NULL),(17,13,'2026-06-28 16:45:16','حشوة أسنان','12','تم إنجاز حشوة أسنان بنجاح للسن رقم 12',125000.00,1,1,50000.00,NULL),(18,13,'2026-06-28 16:45:16','تقويم الأسنان','45','تم إنجاز تقويم الأسنان بنجاح للسن رقم 45',350000.00,1,1,50000.00,NULL),(19,14,'2026-06-06 13:15:16','تنظيف وتلميع','38','تم إنجاز تنظيف وتلميع بنجاح للسن رقم 38',50000.00,0,0,0.00,NULL),(20,16,'2026-07-11 16:00:16','علاج عصب السن','37','تم إنجاز علاج عصب السن بنجاح للسن رقم 37',250000.00,1,2,100000.00,NULL),(21,16,'2026-07-11 16:00:16','تقويم الأسنان','34','تم إنجاز تقويم الأسنان بنجاح للسن رقم 34',300000.00,0,0,0.00,NULL),(22,17,'2026-07-25 11:30:16','فحص دوري','31','تم إنجاز فحص دوري بنجاح للسن رقم 31',125000.00,1,2,100000.00,NULL),(23,17,'2026-07-25 11:30:16','قلع سن','46','تم إنجاز قلع سن بنجاح للسن رقم 46',80000.00,0,0,0.00,NULL),(24,18,'2026-07-02 12:45:16','تبييض الأسنان','41','تم إنجاز تبييض الأسنان بنجاح للسن رقم 41',120000.00,0,0,0.00,NULL),(25,19,'2026-06-20 11:45:16','زيركون ليزري','23','تم إنجاز زيركون ليزري بنجاح للسن رقم 23',400000.00,0,0,0.00,NULL),(26,19,'2026-06-20 11:45:16','تاج / جسر','16','تم إنجاز تاج / جسر بنجاح للسن رقم 16',300000.00,1,2,100000.00,NULL),(27,20,'2026-06-05 14:45:16','زيركون ليزري','17','تم إنجاز زيركون ليزري بنجاح للسن رقم 17',400000.00,0,0,0.00,NULL),(28,21,'2026-07-21 10:30:16','فحص دوري','14','تم إنجاز فحص دوري بنجاح للسن رقم 14',75000.00,1,1,50000.00,NULL),(29,21,'2026-07-21 10:30:16','فحص دوري','13','تم إنجاز فحص دوري بنجاح للسن رقم 13',125000.00,1,2,100000.00,NULL),(30,21,'2026-07-21 10:30:16','علاج عصب السن','24','تم إنجاز علاج عصب السن بنجاح للسن رقم 24',200000.00,1,1,50000.00,NULL),(31,23,'2026-07-23 10:45:16','تنظيف وتلميع','31','تم إنجاز تنظيف وتلميع بنجاح للسن رقم 31',50000.00,0,0,0.00,NULL),(32,24,'2026-06-04 15:15:16','تبييض الأسنان','34','تم إنجاز تبييض الأسنان بنجاح للسن رقم 34',220000.00,1,2,100000.00,NULL),(33,24,'2026-06-04 15:15:16','زيركون ليزري','13','تم إنجاز زيركون ليزري بنجاح للسن رقم 13',450000.00,1,1,50000.00,NULL),(34,24,'2026-06-04 15:15:16','تبييض الأسنان','15','تم إنجاز تبييض الأسنان بنجاح للسن رقم 15',120000.00,0,0,0.00,NULL),(35,25,'2026-06-23 17:15:16','تقويم الأسنان','36','تم إنجاز تقويم الأسنان بنجاح للسن رقم 36',300000.00,0,0,0.00,NULL),(36,25,'2026-06-23 17:15:16','حشوة أسنان','33','تم إنجاز حشوة أسنان بنجاح للسن رقم 33',125000.00,1,1,50000.00,NULL),(37,25,'2026-06-23 17:15:16','فحص دوري','47','تم إنجاز فحص دوري بنجاح للسن رقم 47',25000.00,0,0,0.00,NULL),(38,26,'2026-07-14 17:30:16','علاج عصب السن','28','تم إنجاز علاج عصب السن بنجاح للسن رقم 28',200000.00,1,1,50000.00,NULL),(39,27,'2026-07-17 17:45:16','تبييض الأسنان','45','تم إنجاز تبييض الأسنان بنجاح للسن رقم 45',120000.00,0,0,0.00,NULL),(40,27,'2026-07-17 17:45:16','تبييض الأسنان','16','تم إنجاز تبييض الأسنان بنجاح للسن رقم 16',120000.00,0,0,0.00,NULL),(41,28,'2026-06-23 11:45:16','تنظيف وتلميع','46','تم إنجاز تنظيف وتلميع بنجاح للسن رقم 46',50000.00,0,0,0.00,NULL),(42,29,'2026-07-09 12:30:16','تبييض الأسنان','34','تم إنجاز تبييض الأسنان بنجاح للسن رقم 34',120000.00,0,0,0.00,NULL),(43,29,'2026-07-09 12:30:16','تنظيف وتلميع','11','تم إنجاز تنظيف وتلميع بنجاح للسن رقم 11',50000.00,0,0,0.00,NULL),(44,29,'2026-07-09 12:30:16','قلع سن','33','تم إنجاز قلع سن بنجاح للسن رقم 33',80000.00,0,0,0.00,NULL),(45,31,'2026-07-25 12:45:16','تقويم الأسنان','48','تم إنجاز تقويم الأسنان بنجاح للسن رقم 48',350000.00,1,1,50000.00,NULL),(46,33,'2026-07-11 15:45:16','تنظيف وتلميع','23','تم إنجاز تنظيف وتلميع بنجاح للسن رقم 23',150000.00,1,2,100000.00,NULL),(47,34,'2026-06-11 10:00:16','فحص دوري','23','تم إنجاز فحص دوري بنجاح للسن رقم 23',125000.00,1,2,100000.00,NULL),(48,34,'2026-06-11 10:00:16','قلع سن','34','تم إنجاز قلع سن بنجاح للسن رقم 34',130000.00,1,1,50000.00,NULL),(49,34,'2026-06-11 10:00:16','تاج / جسر','35','تم إنجاز تاج / جسر بنجاح للسن رقم 35',200000.00,0,0,0.00,NULL),(50,36,'2026-06-25 12:30:16','تنظيف وتلميع','25','تم إنجاز تنظيف وتلميع بنجاح للسن رقم 25',50000.00,0,0,0.00,NULL),(51,36,'2026-06-25 12:30:16','تنظيف وتلميع','46','تم إنجاز تنظيف وتلميع بنجاح للسن رقم 46',50000.00,0,0,0.00,NULL),(52,36,'2026-06-25 12:30:16','علاج عصب السن','15','تم إنجاز علاج عصب السن بنجاح للسن رقم 15',250000.00,1,2,100000.00,NULL),(53,38,'2026-07-20 17:00:16','قلع سن','18','تم إنجاز قلع سن بنجاح للسن رقم 18',80000.00,0,0,0.00,NULL),(54,39,'2026-07-17 13:45:16','تنظيف وتلميع','43','تم إنجاز تنظيف وتلميع بنجاح للسن رقم 43',50000.00,0,0,0.00,NULL),(55,39,'2026-07-17 13:45:16','حشوة أسنان','36','تم إنجاز حشوة أسنان بنجاح للسن رقم 36',75000.00,0,0,0.00,NULL),(56,40,'2026-06-21 09:30:16','تاج / جسر','27','تم إنجاز تاج / جسر بنجاح للسن رقم 27',200000.00,0,0,0.00,NULL),(57,40,'2026-06-21 09:30:16','حشوة أسنان','23','تم إنجاز حشوة أسنان بنجاح للسن رقم 23',125000.00,1,1,50000.00,NULL),(58,41,'2026-06-12 14:00:16','قلع سن','47','تم إنجاز قلع سن بنجاح للسن رقم 47',80000.00,0,0,0.00,NULL),(59,41,'2026-06-12 14:00:16','حشوة أسنان','37','تم إنجاز حشوة أسنان بنجاح للسن رقم 37',175000.00,1,2,100000.00,NULL),(60,41,'2026-06-12 14:00:16','زيركون ليزري','11','تم إنجاز زيركون ليزري بنجاح للسن رقم 11',500000.00,1,2,100000.00,NULL),(61,42,'2026-07-01 16:15:16','حشوة أسنان','21','تم إنجاز حشوة أسنان بنجاح للسن رقم 21',175000.00,1,2,100000.00,NULL),(62,42,'2026-07-01 16:15:16','زيركون ليزري','14','تم إنجاز زيركون ليزري بنجاح للسن رقم 14',500000.00,1,2,100000.00,NULL),(63,42,'2026-07-01 16:15:16','زيركون ليزري','17','تم إنجاز زيركون ليزري بنجاح للسن رقم 17',450000.00,1,1,50000.00,NULL),(64,43,'2026-06-27 14:30:16','تبييض الأسنان','42','تم إنجاز تبييض الأسنان بنجاح للسن رقم 42',170000.00,1,1,50000.00,NULL),(65,44,'2026-07-28 10:45:16','تنظيف وتلميع','45','تم إنجاز تنظيف وتلميع بنجاح للسن رقم 45',50000.00,0,0,0.00,NULL),(66,46,'2026-07-13 09:30:16','علاج عصب السن','34','تم إنجاز علاج عصب السن بنجاح للسن رقم 34',150000.00,0,0,0.00,NULL),(67,46,'2026-07-13 09:30:16','تبييض الأسنان','18','تم إنجاز تبييض الأسنان بنجاح للسن رقم 18',170000.00,1,1,50000.00,NULL),(68,47,'2026-06-18 13:00:16','زيركون ليزري','31','تم إنجاز زيركون ليزري بنجاح للسن رقم 31',450000.00,1,1,50000.00,NULL),(69,47,'2026-06-18 13:00:16','تقويم الأسنان','11','تم إنجاز تقويم الأسنان بنجاح للسن رقم 11',400000.00,1,2,100000.00,NULL),(70,47,'2026-06-18 13:00:16','تاج / جسر','45','تم إنجاز تاج / جسر بنجاح للسن رقم 45',250000.00,1,1,50000.00,NULL),(71,48,'2026-06-17 16:00:16','علاج عصب السن','22','تم إنجاز علاج عصب السن بنجاح للسن رقم 22',200000.00,1,1,50000.00,NULL),(72,49,'2026-07-05 15:15:16','تنظيف وتلميع','18','تم إنجاز تنظيف وتلميع بنجاح للسن رقم 18',150000.00,1,2,100000.00,NULL),(73,49,'2026-07-05 15:15:16','حشوة أسنان','47','تم إنجاز حشوة أسنان بنجاح للسن رقم 47',175000.00,1,2,100000.00,NULL),(74,50,'2026-06-06 13:15:16','قلع سن','34','تم إنجاز قلع سن بنجاح للسن رقم 34',180000.00,1,2,100000.00,NULL),(75,50,'2026-06-06 13:15:16','قلع سن','16','تم إنجاز قلع سن بنجاح للسن رقم 16',130000.00,1,1,50000.00,NULL),(76,50,'2026-06-06 13:15:16','تبييض الأسنان','27','تم إنجاز تبييض الأسنان بنجاح للسن رقم 27',170000.00,1,1,50000.00,NULL),(77,51,'2026-06-24 09:45:16','قلع سن','44','تم إنجاز قلع سن بنجاح للسن رقم 44',80000.00,0,0,0.00,NULL),(78,51,'2026-06-24 09:45:16','حشوة أسنان','22','تم إنجاز حشوة أسنان بنجاح للسن رقم 22',75000.00,0,0,0.00,NULL),(79,52,'2026-07-28 17:15:16','زيركون ليزري','22','تم إنجاز زيركون ليزري بنجاح للسن رقم 22',450000.00,1,1,50000.00,NULL),(80,53,'2026-06-18 16:15:16','فحص دوري','16','تم إنجاز فحص دوري بنجاح للسن رقم 16',125000.00,1,2,100000.00,NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'mazen','scrypt:32768:8:1$0ZnCpOx4UUiwItgG$b6dc81517fe860752e561e78b57cb3474f8bb8310ae56ddd8531c970426d0e40ca11ffcc1cc4171543719af4a654712e708d1e2e81181656b8a7bb974167534b','admin','مازن','الشب',NULL,NULL),(2,'رند','scrypt:32768:8:1$2ShEFynmMI74D0ah$d8b6fee88bc07d4439c73ee0e2296ff7bf185f85c932470f35201a5c1ce3c118c13a5bb092c9fcf9f85803b0404fe0e8a4db827490e1a53a34dbcb86317e5932','receptionist','رند','سالم',NULL,NULL),(3,'nasip','scrypt:32768:8:1$cpURlIJkYkXdVH4l$8b1ff339f2771289a7f6bd504ffe0f5c9249280cd836918cc300d541124e7df01d7f147bef704d2574ed2b4fa4fb6f7257a598408fea2cd83baa470a900e9e5b','patient','نسيب','جبارة',1,'nasip123'),(4,'jana','scrypt:32768:8:1$7PTKu4JOX6jvrNLV$0444c87daa1f5d9ddace0c494f5758b810bfce068091ad7f2c0685ef6dd75f6dc720262aded7f99cb5d7b1f2010b74342d5ad81ac4da4acbb0d416e4a2143072','patient','جنا','عديرة',2,'jana123'),(5,'ahmad','scrypt:32768:8:1$80YVhAaz8sfCknmb$3a82c4967d68b6a7f0391d99639fee81d7a49e6a863696aafe45509426968679923c10d56244dea293f70a74f597e7b97a10b5f404038d62a92f00ab14f3a88e','doctor','أحمد','السالم',NULL,NULL);
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

-- Dump completed on 2026-08-04 16:56:19
