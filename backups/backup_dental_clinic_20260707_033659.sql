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
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `appointment_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appointment`
--

LOCK TABLES `appointment` WRITE;
/*!40000 ALTER TABLE `appointment` DISABLE KEYS */;
INSERT INTO `appointment` VALUES (1,1,'2026-06-21 10:00:00','Check-up','Cancelled',NULL),(2,2,'2026-06-22 10:00:00','Cleaning','Cancelled',NULL),(3,3,'2026-06-23 10:00:00','Filling','Cancelled',NULL),(4,4,'2026-06-24 10:00:00','Root Canal','Cancelled',NULL),(5,5,'2026-06-25 10:00:00','Extraction','Cancelled',NULL),(6,6,'2026-06-26 10:00:00','Check-up','Cancelled',NULL),(7,7,'2026-06-27 10:00:00','Cleaning','Cancelled',NULL),(8,8,'2026-06-28 10:00:00','Filling','Cancelled',NULL),(9,9,'2026-06-29 10:00:00','Check-up','Cancelled',NULL),(10,10,'2026-06-30 10:00:00','Follow-up','Cancelled',NULL),(11,1,'2026-06-20 16:00:00','Check-up','Done',NULL),(12,9,'2026-06-24 12:00:00','Extraction','Cancelled',NULL),(13,8,'2026-06-24 11:00:00','Whitening','Cancelled',NULL),(15,8,'2026-06-22 17:10:00','Extraction','Done',NULL),(16,2,'2026-06-22 17:25:00','Emergency Pain','Done',NULL),(17,10,'2026-06-27 11:00:00','Root Canal','Cancelled',NULL),(18,1,'2026-07-07 16:00:00','Check-up','Done','2026-07-06 05:43:00'),(19,10,'2026-07-06 12:00:00','Extraction','Done','2026-07-06 06:54:58'),(20,9,'2026-07-06 12:00:00','Crown / Bridge','Done','2026-07-06 07:05:06'),(21,3,'2026-07-06 12:00:00','Whitening','Cancelled',NULL),(22,6,'2026-07-06 13:00:00','Emergency Pain','Done','2026-07-06 07:09:06');
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
  `amount` float NOT NULL,
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
INSERT INTO `expense` VALUES (1,'Rent',1000000,'2026-07-06','rent');
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
  `tax_rate` decimal(5,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `appointment_id` (`appointment_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `invoice_ibfk_1` FOREIGN KEY (`appointment_id`) REFERENCES `appointment` (`id`),
  CONSTRAINT `invoice_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice`
--

LOCK TABLES `invoice` WRITE;
/*!40000 ALTER TABLE `invoice` DISABLE KEYS */;
INSERT INTO `invoice` VALUES (1,11,1,'2026-06-20 15:24:52',0.00,'value',0.00),(2,15,8,'2026-06-22 17:19:01',0.00,'value',0.00),(3,16,2,'2026-06-22 17:25:56',10.00,'percentage',0.00),(4,18,1,'2026-07-06 05:49:02',0.00,'value',0.00),(5,19,10,'2026-07-06 06:59:39',0.00,'value',0.00),(6,20,9,'2026-07-06 07:05:18',0.00,'value',0.00),(8,22,6,'2026-07-06 21:09:37',0.00,'value',0.00);
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
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient`
--

LOCK TABLES `patient` WRITE;
/*!40000 ALTER TABLE `patient` DISABLE KEYS */;
INSERT INTO `patient` VALUES (1,NULL,'أحمد','العلي',NULL,'1990-05-15','Male','+963958948721','ahmed.ali@example.com','المزة','دمشق',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(2,NULL,'فاطمة','الحسن',NULL,'1995-08-20','Female','+963958948722','fatima.hassan@example.com','الشهباء','حلب',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(3,NULL,'محمد','المصري',NULL,'1988-12-10','Male','+963958948723','mohammad.masri@example.com','الإنشاءات','حمص',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(4,NULL,'سارة','الخالد',NULL,'1992-03-05','Female','+963958948724','sara.khaled@example.com','المشروع الأول','اللاذقية',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(5,NULL,'خالد','اليوسف',NULL,'1985-07-25','Male','+963958948725','khaled.youssef@example.com','الشريعة','حماة',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(6,NULL,'نور','الخطيب',NULL,'1998-10-18','Female','+963958948726','nour.khatib@example.com','الكورنيش','طرطوس',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(7,NULL,'يوسف','سليمان',NULL,'1991-01-30','Male','+963958948727','youssef.sleiman@example.com','أبو رمانة','دمشق',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(8,NULL,'منى','عبود',NULL,'1987-09-12','Female','+963958948728','mona.abboud@example.com','طريق قنوات','السويداء',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(9,NULL,'سامر','حنا',NULL,'1983-04-22','Male','+963958948729','samer.hanna@example.com','باب توما','دمشق',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(10,NULL,'رشا','الراعي',NULL,'1994-11-02','Female','+963958948730','rasha.raei@example.com','الحمراء','حمص',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
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
  CONSTRAINT `patient_file_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient_file`
--

LOCK TABLES `patient_file` WRITE;
/*!40000 ALTER TABLE `patient_file` DISABLE KEYS */;
INSERT INTO `patient_file` VALUES (2,10,'jaw.jpg','uploads/patients/fd593a4f6ce64161bc87f8961e534c64.jpg','image/jpeg','2026-07-06 06:16:07','فك');
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
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
INSERT INTO `payment` VALUES (1,1,150000.00,'2026-06-20 15:28:15',''),(2,8,160000.00,'2026-06-22 17:21:00','لا يوجد'),(3,2,200000.00,'2026-06-22 17:27:03',''),(4,2,70000.00,'2026-06-22 17:34:43',''),(5,9,400000.00,'2026-07-06 07:10:59',''),(6,10,100000.00,'2026-07-06 07:12:51','');
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
  CONSTRAINT `payment_allocation_ibfk_1` FOREIGN KEY (`payment_id`) REFERENCES `payment` (`id`),
  CONSTRAINT `payment_allocation_ibfk_2` FOREIGN KEY (`invoice_id`) REFERENCES `invoice` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_allocation`
--

LOCK TABLES `payment_allocation` WRITE;
/*!40000 ALTER TABLE `payment_allocation` DISABLE KEYS */;
INSERT INTO `payment_allocation` VALUES (2,2,2,160000.00),(4,3,3,200000.00),(5,4,3,70000.00),(7,1,1,150000.00),(8,5,6,400000.00),(13,6,5,100000.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_setting`
--

LOCK TABLES `system_setting` WRITE;
/*!40000 ALTER TABLE `system_setting` DISABLE KEYS */;
INSERT INTO `system_setting` VALUES (1,'clinic_name','Clinic'),(2,'clinic_phone','+963 958 948 727'),(3,'clinic_email','kh.nasipdragon@gmail.com'),(4,'clinic_address','Damascus, Syria'),(5,'currency_symbol','S.P'),(6,'default_appointment_duration','30'),(7,'working_hours_start','09:00'),(8,'working_hours_end','18:00'),(9,'working_days','0,1,2,3,4,6'),(10,'treatment_prices','{\"Check-up\": 25000, \"Cleaning\": 50000, \"Filling\": 75000, \"Root Canal\": 150000, \"Extraction\": 80000, \"Crown / Bridge\": 200000, \"Braces / Orthodontics\": 300000, \"Whitening\": 120000, \"Emergency Pain\": 60000, \"Follow-up\": 20000}'),(11,'notification_enable_sms','false'),(12,'notification_enable_whatsapp','false'),(13,'notification_enable_email','false'),(14,'twilio_account_sid',''),(15,'twilio_auth_token',''),(16,'twilio_phone_number',''),(17,'twilio_whatsapp_number',''),(18,'smtp_host','smtp.gmail.com'),(19,'smtp_port','587'),(20,'smtp_user',''),(21,'smtp_password',''),(22,'smtp_from_email',''),(23,'tax_rate','15'),(24,'clinic_vat_number',''),(25,'booking_window_days','35');
/*!40000 ALTER TABLE `system_setting` ENABLE KEYS */;
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
  PRIMARY KEY (`id`),
  KEY `appointment_id` (`appointment_id`),
  CONSTRAINT `treatment_ibfk_1` FOREIGN KEY (`appointment_id`) REFERENCES `appointment` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `treatment`
--

LOCK TABLES `treatment` WRITE;
/*!40000 ALTER TABLE `treatment` DISABLE KEYS */;
INSERT INTO `treatment` VALUES (1,11,'2026-06-20 16:00:00','Filling','1','',75000.00),(2,11,'2026-06-20 16:00:00','Filling','2','',75000.00),(3,15,'2026-06-22 17:10:00','Extraction','1','تخدير موضعي',80000.00),(4,15,'2026-06-22 17:10:00','Extraction','2','',80000.00),(5,16,'2026-06-22 17:25:00','Root Canal','1','',150000.00),(6,16,'2026-06-22 17:25:00','Root Canal','2','',150000.00),(7,18,'2026-07-07 16:00:00','Cleaning','3','',50000.00),(8,18,'2026-07-07 16:00:00','Root Canal','1','',150000.00),(9,19,'2026-07-06 12:00:00','Cleaning','1, 2','',100000.00),(10,20,'2026-07-06 12:00:00','Crown / Bridge','1','',200000.00),(11,20,'2026-07-06 12:00:00','Crown / Bridge','2','',200000.00),(12,22,'2026-07-06 13:00:00','Extraction','1','',80000.00),(13,22,'2026-07-06 13:00:00','Root Canal','2','',150000.00);
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
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `user_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin','scrypt:32768:8:1$atJj4C9ImjWZMGAA$660215c4e032bf012c87e69184d2e4d22e4e97a8237b3e4748e7b1d35545a3d4e89ce3961ad883c8b286e91288fcc98e909aa7ab829ca91dc6362adda6c97312','admin','Admin','User',NULL,NULL),(2,'hiba','scrypt:32768:8:1$h5VJrby7WCgxUyO6$c6685f4b248a4c4675ee3d61b7e9ccafbc9c50a43e330096bac3c4dff9024188c63c69382e650bd92a72e5e178795e80e95e60c8cba59027cce107788975db93','receptionist','Hiba','Ali',NULL,NULL),(3,'rasha','scrypt:32768:8:1$mUnwXn5y7ca6hg5J$dd9dfe6bcb1ed96006eaa9790ee856cf905c8b0b8349bf189b2b658169bc5da2a777abb162f71c07d31b596f09d100b905a3144454f051ed12cf762fdf242849','patient','رشا','الراعي',10,'rasha123');
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

-- Dump completed on 2026-07-07  3:36:59
