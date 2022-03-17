-- ---------------------------------------------------------------------------------------------------------------------
-- WARNING: BACKUP YOUR DATABASE BEFORE UPGRADING
-- THIS SCRIPT IS ONLY FOR UPGRADING 1.8.2 TO 1.9.0
-- THE CURRENT VERSION CAN BE FOUND AT `myems_system_db`.`tbl_versions`
-- ---------------------------------------------------------------------------------------------------------------------

START TRANSACTION;

CREATE DATABASE IF NOT EXISTS `myems_production_db` CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_unicode_ci' ;
USE `myems_production_db` ;

CREATE TABLE IF NOT EXISTS `myems_production_db`.`tbl_products` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(128) NOT NULL,
  `uuid` CHAR(36) NOT NULL,
  `unit_of_measure` VARCHAR(32) NOT NULL,
  `tag` VARCHAR(128) NOT NULL,
  `standard_product_coefficient` DECIMAL(18, 3) NOT NULL DEFAULT 1.0,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_products_index_1` ON  `myems_production_db`.`tbl_products`  (`name`);

CREATE TABLE IF NOT EXISTS `myems_production_db`.`tbl_shifts` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `shopfloor_id` BIGINT NOT NULL,
  `team_id` BIGINT NOT NULL,
  `product_id` BIGINT NOT NULL,
  `product_count` INT NOT NULL,
  `start_datetime_utc` DATETIME NOT NULL,
  `end_datetime_utc` DATETIME NOT NULL,
  `reference_timestamp` DATETIME NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_shifts_index_1` ON  `myems_production_db`.`tbl_shifts`  (`shopfloor_id`, `product_id`, `end_datetime_utc` );
CREATE INDEX `tbl_shifts_index_2` ON  `myems_production_db`.`tbl_shifts`  (`shopfloor_id`, `product_id`,  `start_datetime_utc`, `end_datetime_utc` );
CREATE INDEX `tbl_shifts_index_3` ON  `myems_production_db`.`tbl_shifts`  (`shopfloor_id`, `reference_timestamp`);
CREATE INDEX `tbl_shifts_index_4` ON  `myems_production_db`.`tbl_shifts`  (`shopfloor_id`, `team_id`);

CREATE TABLE IF NOT EXISTS `myems_production_db`.`tbl_shopfloor_hourly` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `shopfloor_id` BIGINT NOT NULL,
  `start_datetime_utc` DATETIME NOT NULL,
  `product_id` BIGINT NOT NULL,
  `product_count` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_shopfloor_hourly_index_1` ON  `myems_production_db`.`tbl_shopfloor_hourly`  (`shopfloor_id`,  `product_id`, `start_datetime_utc`);

CREATE TABLE IF NOT EXISTS `myems_production_db`.`tbl_shopfloor_working_days` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `shopfloor_id` BIGINT NOT NULL,
  `date_local` DATE NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_shopfloor_working_days_index_1` ON  `myems_production_db`.`tbl_shopfloor_working_days`  (`shopfloor_id`, `date_local`);

CREATE TABLE IF NOT EXISTS `myems_production_db`.`tbl_shopfloors_products` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `shopfloor_id` BIGINT NOT NULL,
  `product_id` BIGINT NOT NULL,
  PRIMARY KEY (`id`));

CREATE TABLE IF NOT EXISTS `myems_production_db`.`tbl_shopfloors_teams` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `shopfloor_id` BIGINT NOT NULL,
  `team_id` BIGINT NOT NULL,
  PRIMARY KEY (`id`));

CREATE TABLE IF NOT EXISTS `myems_production_db`.`tbl_teams` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(128) NOT NULL,
  `uuid` CHAR(36) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_teams_index_1` ON  `myems_production_db`.`tbl_teams`   (`name`);

-- UPDATE VERSION NUMBER
USE `myems_system_db` ;
UPDATE `myems_system_db`.`tbl_versions` SET version='1.9.0', release_date='2022-03-28' WHERE id=1;

COMMIT;
