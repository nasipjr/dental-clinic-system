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
) ENGINE=InnoDB AUTO_INCREMENT=1714 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appointment`
--

LOCK TABLES `appointment` WRITE;
/*!40000 ALTER TABLE `appointment` DISABLE KEYS */;
INSERT INTO `appointment` VALUES (1713,349,'2026-08-14 19:09:43','جلسة جديدة سريعة','Done','2026-08-14 19:09:43',19,30);
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
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=371 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice`
--

LOCK TABLES `invoice` WRITE;
/*!40000 ALTER TABLE `invoice` DISABLE KEYS */;
INSERT INTO `invoice` VALUES (370,1713,349,'2026-08-14 19:10:06',0.00,'value',0.00,0.00,NULL);
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
  KEY `fk_patient_primary_doctor` (`primary_doctor_id`)
) ENGINE=InnoDB AUTO_INCREMENT=350 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient`
--

LOCK TABLES `patient` WRITE;
/*!40000 ALTER TABLE `patient` DISABLE KEYS */;
INSERT INTO `patient` VALUES (349,'mr','نسيب','جبارة',NULL,'2002-06-10','Male','+963958948727','kh.nasipdragon@gmail.com','اللاذقية استراد الزراعة','اللاذقية',NULL,NULL,'سوريا','لا يوجد','تحسس من الديكلون',NULL,'مهندس',NULL,NULL,'932284186',1,NULL);
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
  `invoice_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1097 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
INSERT INTO `payment` VALUES (1096,349,360000.00,'2026-08-14 19:29:49','',370);
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
) ENGINE=InnoDB AUTO_INCREMENT=374 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_allocation`
--

LOCK TABLES `payment_allocation` WRITE;
/*!40000 ALTER TABLE `payment_allocation` DISABLE KEYS */;
INSERT INTO `payment_allocation` VALUES (373,1096,370,360000.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=666 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_setting`
--

LOCK TABLES `system_setting` WRITE;
/*!40000 ALTER TABLE `system_setting` DISABLE KEYS */;
INSERT INTO `system_setting` VALUES (606,'clinic_name','نسيب جبارة'),(607,'clinic_phone','+963 958 948 727'),(608,'clinic_email','kh.nasipdragon@gmail.com'),(609,'clinic_address','Latakia, Syria'),(610,'developer_whatsapp','963958948727'),(611,'currency_symbol','SP'),(612,'default_appointment_duration','30'),(613,'auto_cancel_expired_minutes','120'),(614,'auto_close_open_session_minutes',''),(615,'working_hours_start','09:00'),(616,'working_hours_end','19:00'),(617,'working_days','0,1,2,3,4,5,6'),(618,'treatment_prices','{\"حشوة ضوئية كومبوزيت\": {\"price\": 60000, \"duration\": 30, \"active\": true, \"category\": \"حشوات ومعالجات تجميلية\"}, \"تنظيف وتلميع الأسنان وتقليح\": {\"price\": 50000, \"duration\": 30, \"active\": true, \"category\": \"حشوات ومعالجات تجميلية\"}, \"حشوة تجميلية\": {\"price\": 200000, \"duration\": 30, \"active\": true, \"category\": \"حشوات ومعالجات تجميلية\"}, \"حشوة ضوئية كومبوزيت (سطح واحد)\": {\"price\": 60000, \"duration\": 30, \"active\": true, \"category\": \"حشوات ومعالجات تجميلية\"}, \"حشوة ضوئية كومبوزيت (عدة سطوح)\": {\"price\": 85000, \"duration\": 40, \"active\": true, \"category\": \"حشوات ومعالجات تجميلية\"}, \"حشوة أملغم ملغمية\": {\"price\": 55000, \"duration\": 30, \"active\": true, \"category\": \"حشوات ومعالجات تجميلية\"}, \"تبييض الأسنان بالليزر/الضوء\": {\"price\": 120000, \"duration\": 45, \"active\": true, \"category\": \"حشوات ومعالجات تجميلية\"}, \"عدسات فينير تجميلية\": {\"price\": 250000, \"duration\": 45, \"active\": true, \"category\": \"حشوات ومعالجات تجميلية\"}, \"جلسة سحب عصب وتنظيف قنوات\": {\"price\": 200000, \"duration\": 45, \"active\": true, \"category\": \"علاج عصب وجذور\"}, \"حشو قنوات وحشو نهائي (عصب)\": {\"price\": 150000, \"duration\": 45, \"active\": true, \"category\": \"علاج عصب وجذور\"}, \"إعادة علاج عصب سابق\": {\"price\": 180000, \"duration\": 50, \"active\": true, \"category\": \"علاج عصب وجذور\"}, \"وتد فايبر مع حشوة بناء\": {\"price\": 100000, \"duration\": 35, \"active\": true, \"category\": \"علاج عصب وجذور\"}, \"قلع سن عادي\": {\"price\": 80000, \"duration\": 30, \"active\": true, \"category\": \"جراحة وقلع\"}, \"معالجة ما بعد القلع\": {\"price\": 30000, \"duration\": 20, \"active\": true, \"category\": \"جراحة وقلع\"}, \"قلع جراحي / ضرس عقل انحشاري\": {\"price\": 180000, \"duration\": 45, \"active\": true, \"category\": \"جراحة وقلع\"}, \"زرع سن (زرعة تيتانيوم)\": {\"price\": 450000, \"duration\": 60, \"active\": true, \"category\": \"جراحة وقلع\"}, \"طعوم عظمية ورفع جيب فكي\": {\"price\": 350000, \"duration\": 60, \"active\": true, \"category\": \"جراحة وقلع\"}, \"تاج زيركون / بورسلين\": {\"price\": 200000, \"duration\": 45, \"active\": true, \"category\": \"تعويضات وتيجان\"}, \"جسر أسنان ثابت\": {\"price\": 350000, \"duration\": 50, \"active\": true, \"category\": \"تعويضات وتيجان\"}, \"تاج إيماكس تجميلي\": {\"price\": 230000, \"duration\": 45, \"active\": true, \"category\": \"تعويضات وتيجان\"}, \"طقم أسنان متحرك كاملاً\": {\"price\": 350000, \"duration\": 50, \"active\": true, \"category\": \"تعويضات وتيجان\"}, \"طقم أسنان جزئي هيكلي\": {\"price\": 250000, \"duration\": 40, \"active\": true, \"category\": \"تعويضات وتيجان\"}, \"طبعة أسنان وتأطير\": {\"price\": 40000, \"duration\": 25, \"active\": true, \"category\": \"تعويضات وتيجان\"}, \"تركيب تقويم أسنان\": {\"price\": 600000, \"duration\": 60, \"active\": true, \"category\": \"تقويم أسنان\"}, \"جلسة شد وتفقد تقويم\": {\"price\": 35000, \"duration\": 20, \"active\": true, \"category\": \"تقويم أسنان\"}, \"فك تقويم وتثبيت\": {\"price\": 120000, \"duration\": 40, \"active\": true, \"category\": \"تقويم أسنان\"}, \"تقويم شفاف (صينية)\": {\"price\": 750000, \"duration\": 45, \"active\": true, \"category\": \"تقويم أسنان\"}, \"حشوة أطفال مخصصة\": {\"price\": 45000, \"duration\": 25, \"active\": true, \"category\": \"أسنان أطفال\"}, \"بتر عصب أطفال (سحب عصب لببي)\": {\"price\": 70000, \"duration\": 30, \"active\": true, \"category\": \"أسنان أطفال\"}, \"حافظ مسافة للأطفال\": {\"price\": 80000, \"duration\": 30, \"active\": true, \"category\": \"أسنان أطفال\"}, \"تغليف ميازيب وقائي\": {\"price\": 35000, \"duration\": 20, \"active\": true, \"category\": \"أسنان أطفال\"}, \"فحص دوري واستشارة\": {\"price\": 25000, \"duration\": 20, \"active\": true, \"category\": \"إجراءات عامة وأخرى\"}, \"صورة بانورامية للأسنان\": {\"price\": 50000, \"duration\": 20, \"active\": true, \"category\": \"إجراءات عامة وأخرى\"}, \"أشعة سينية (شعاعية)\": {\"price\": 20000, \"duration\": 15, \"active\": true, \"category\": \"إجراءات عامة وأخرى\"}, \"كشف ألم طارئ\": {\"price\": 60000, \"duration\": 30, \"active\": true, \"category\": \"إجراءات عامة وأخرى\"}, \"متابعة دورية\": {\"price\": 20000, \"duration\": 15, \"active\": true, \"category\": \"إجراءات عامة وأخرى\"}, \"تطبيق فلورايد وقائي\": {\"price\": 30000, \"duration\": 15, \"active\": true, \"category\": \"إجراءات عامة وأخرى\"}, \"معالجة حساسيات الأسنان\": {\"price\": 35000, \"duration\": 20, \"active\": true, \"category\": \"إجراءات عامة وأخرى\"}, \"واقي ليلي ضد الصرير\": {\"price\": 100000, \"duration\": 30, \"active\": true, \"category\": \"إجراءات عامة وأخرى\"}, \"علاج التهابات اللثة\": {\"price\": 60000, \"duration\": 30, \"active\": true, \"category\": \"إجراءات عامة وأخرى\"}, \"شهادة تقرير طبي\": {\"price\": 25000, \"duration\": 15, \"active\": true, \"category\": \"إجراءات عامة وأخرى\"}}'),(619,'anesthesia_needle_price','50000.0'),(620,'notification_enable_sms','false'),(621,'notification_enable_telegram','true'),(622,'notification_enable_email','false'),(623,'telegram_bot_token','8732677418:AAGqRTIJyPDl4-mbTGEuoGLcsgF3yUlGha4'),(624,'telegram_24h_enabled','true'),(625,'telegram_2h_enabled','true'),(626,'telegram_24h_template','تذكير موعد من {clinic_name}: مرحباً {المريض_name}، نود تذكيركم بموعدكم غداً بتاريخ {الموعد_الوقت}. نتمنى لكم السلامة.'),(627,'telegram_2h_template','تذكير موعد من {clinic_name}: مرحباً {المريض_name}، نود تذكيركم بموعدكم اليوم بعد ساعتين في تمام الساعة {الموعد_الوقت}. بانتظاركم.'),(628,'commpeak_api_key',''),(629,'commpeak_stream_id',''),(630,'smtp_host','smtp.gmail.com'),(631,'smtp_port','587'),(632,'smtp_user',''),(633,'smtp_password',''),(634,'smtp_from_email',''),(635,'email_24h_enabled','true'),(636,'email_2h_enabled','true'),(637,'email_24h_subject','تذكير بموعدك لدى {clinic_name}'),(638,'email_24h_template','عزيزي {المريض_name}،\r\n\r\nهذا تذكير بموعدك لدى {clinic_name} غداً بتاريخ {الموعد_الوقت}.\r\n\r\nنتمنى لكم السلامة.\r\n\r\nمع تحيات،\r\n{clinic_name}'),(639,'email_2h_subject','تذكير بموعدك لدى {clinic_name}'),(640,'email_2h_template','عزيزي {المريض_name}،\r\n\r\nهذا تذكير بموعدك لدى {clinic_name} اليوم بعد ساعتين في تمام الساعة {الموعد_الوقت}.\r\n\r\nبانتظاركم.\r\n\r\nمع تحيات،\r\n{clinic_name}'),(641,'sms_24h_enabled','true'),(642,'sms_2h_enabled','true'),(643,'sms_24h_template','تذكير من {clinic_name}: موعدك بتاريخ {الموعد_الوقت}. يرجى الحضور في الوقت المحدد.'),(644,'sms_2h_template','تذكير من {clinic_name}: موعدك بتاريخ {الموعد_الوقت}. يرجى الحضور في الوقت المحدد.'),(645,'sms_cancel_enabled','true'),(646,'sms_reschedule_enabled','true'),(647,'telegram_cancel_enabled','true'),(648,'telegram_reschedule_enabled','true'),(649,'email_cancel_enabled','true'),(650,'email_reschedule_enabled','true'),(651,'sms_cancel_template','تنبيه من {clinic_name}: تم إلغاء موعدك المحدد بتاريخ {الموعد_الوقت}.'),(652,'sms_reschedule_template','تنبيه من {clinic_name}: تم تعديل موعدك ليصبح بتاريخ {الموعد_الوقت}. يرجى الحضور في الوقت المحدد.'),(653,'telegram_cancel_template','تنبيه من {clinic_name}: تم إلغاء موعدك المحدد بتاريخ {الموعد_الوقت}. نتمنى لكم السلامة.'),(654,'telegram_reschedule_template','تنبيه من {clinic_name}: تم تعديل موعدك ليصبح بتاريخ {الموعد_الوقت}. يرجى الحضور في الوقت المحدد.'),(655,'email_cancel_subject','إلغاء الموعد - {clinic_name}'),(656,'email_cancel_template','عزيزي {المريض_name}،\r\n\r\nنود إعلامكم بأنه تم إلغاء موعدكم المحدد بتاريخ {الموعد_الوقت}.\r\n\r\nنتمنى لكم السلامة.\r\n\r\nمع تحيات،\r\n{clinic_name}'),(657,'email_reschedule_subject','تعديل موعدك لدى {clinic_name}'),(658,'email_reschedule_template','عزيزي {المريض_name}،\r\n\r\nنود إعلامكم بأنه تم تعديل موعدكم ليصبح بتاريخ {الموعد_الوقت}.\r\n\r\nيرجى الحضور في الوقت المحدد.\r\n\r\nمع تحيات،\r\n{clinic_name}'),(659,'tax_rate','15'),(660,'clinic_vat_number',''),(661,'booking_window_days','60'),(662,'active_license_key','DCMS-T30-20260913-1DECA8A9DA'),(663,'auto_trial_created_at','2026-08-14 18:31:51'),(664,'last_system_activity','2026-08-14 19:31:40'),(665,'anesthesia_types','[{\"name\": \"\\u062a\\u062e\\u062f\\u064a\\u0631 \\u0627\\u0631\\u062a\\u0634\\u0627\\u062d\\u064a (\\u0625\\u0628\\u0631\\u0629 \\u0642\\u0635\\u064a\\u0631\\u0629)\", \"price\": 50000.0}, {\"name\": \"\\u062a\\u062e\\u062f\\u064a\\u0631 \\u062d\\u0635\\u0631\\u064a / \\u0646\\u0627\\u0635\\u0641\\u064a (\\u0625\\u0628\\u0631\\u0629 \\u0637\\u0648\\u064a\\u0644\\u0629)\", \"price\": 60000.0}, {\"name\": \"\\u062a\\u062e\\u062f\\u064a\\u0631 \\u0645\\u0648\\u0636\\u0639\\u064a (\\u0633\\u0637\\u062d\\u064a / \\u062c\\u0644)\", \"price\": 25000.0}, {\"name\": \"\\u062a\\u062e\\u062f\\u064a\\u0631 \\u062e\\u0627\\u0635 \\u0644\\u0644\\u0623\\u0637\\u0641\\u0627\\u0644\", \"price\": 45000.0}]');
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
) ENGINE=InnoDB AUTO_INCREMENT=414 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
  `anesthesia_type` varchar(150) DEFAULT NULL,
  `doctor_id` int DEFAULT NULL,
  `salary_expense_id` int DEFAULT NULL,
  `teeth_range` varchar(100) DEFAULT NULL,
  `quadrant` varchar(50) DEFAULT NULL,
  `jaw` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `appointment_id` (`appointment_id`),
  KEY `doctor_id` (`doctor_id`),
  KEY `salary_expense_id` (`salary_expense_id`),
  CONSTRAINT `treatment_ibfk_1` FOREIGN KEY (`appointment_id`) REFERENCES `appointment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `treatment_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `user` (`id`),
  CONSTRAINT `treatment_ibfk_3` FOREIGN KEY (`salary_expense_id`) REFERENCES `expense` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=516 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `treatment`
--

LOCK TABLES `treatment` WRITE;
/*!40000 ALTER TABLE `treatment` DISABLE KEYS */;
INSERT INTO `treatment` VALUES (513,1713,'2026-08-14 19:10:06','جلسة سحب عصب وتنظيف قنوات','18','',200000.00,0,0,0.00,NULL,19,NULL,NULL,NULL,NULL),(514,1713,'2026-08-14 19:19:03','قلع سن عادي','17','',130000.00,1,1,50000.00,'تخدير ارتشاحي (إبرة قصيرة)',19,NULL,NULL,NULL,NULL),(515,1713,'2026-08-14 19:26:47','معالجة ما بعد القلع','17','',30000.00,0,0,0.00,NULL,19,NULL,NULL,NULL,NULL);
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
  KEY `fk_user_patient` (`patient_id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (19,'admin','scrypt:32768:8:1$Egv8fkFG9Jbt4uSI$771ef418aec69d6e4863e99bdc8a879d76377b87e8961748e9335c504b8a0233f4aefb721f68a7a937b9e23cb0932b98a4d24f1ddbc1d360169d0908445f59bd','admin','نسيب','جبارة',NULL,NULL);
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

-- Dump completed on 2026-08-14 19:32:03
