SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `projectfflogs` DEFAULT CHARACTER SET utf8 ;
USE `projectfflogs` ;

-- -----------------------------------------------------
-- Table `projectfflogs`.`user`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `projectfflogs`.`user` (
  `id_user` INT(11) NOT NULL ,
  `user_name` VARCHAR(255) NOT NULL ,
  PRIMARY KEY (`id_user`) ,
  UNIQUE INDEX `id_user_UNIQUE` (`id_user` ASC) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'Information about fflog account : user name and id.';


-- -----------------------------------------------------
-- Table `projectfflogs`.`character`
-- -----------------------------------------------------
-- *** Update : fk_id_user deleted : protected data
-- *** Update 2 : field data_center replace by 'region' and 'slug'
CREATE  TABLE IF NOT EXISTS `projectfflogs`.`character` (
  `id_character` INT(11) NOT NULL ,
  `character_name` VARCHAR(255) NOT NULL ,
  `server` VARCHAR(255) ,
  `region` VARCHAR(255) ,
  `slug` VARCHAR(255) ,
  PRIMARY KEY (`id_character`) ,
  UNIQUE INDEX `id_character_UNIQUE` (`id_character` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'Player characters who are in reports. A player can have several characters and a character can be linked to no fflog account (so no player in fflog).';


-- -----------------------------------------------------
-- Table `projectfflogs`.`jobtype`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `projectfflogs`.`jobtype` (
  `id_job_type` INT(11) NOT NULL ,
  `job_type_name` VARCHAR(255) NOT NULL ,
  PRIMARY KEY (`id_job_type`) ,
  UNIQUE INDEX `id_job_type_UNIQUE` (`id_job_type` ASC) ,
  UNIQUE INDEX `job_type_name_UNIQUE` (`job_type_name` ASC) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'Type of a job in the game : tank, healer, melee, range, caster.';


-- -----------------------------------------------------
-- Table `projectfflogs`.`job`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `projectfflogs`.`job` (
  `id_job` INT(11) NOT NULL ,
  `job_name` VARCHAR(45) NOT NULL ,
  `fk_id_job_type` INT(11) NOT NULL ,
  PRIMARY KEY (`id_job`) ,
  UNIQUE INDEX `id_job_UNIQUE` (`id_job` ASC) ,
  UNIQUE INDEX `job_name_UNIQUE` (`job_name` ASC) ,
  INDEX `fk_id_job_type_idx` (`fk_id_job_type` ASC) ,
  CONSTRAINT `fk_id_job_type`
    FOREIGN KEY (`fk_id_job_type` )
    REFERENCES `projectfflogs`.`jobtype` (`id_job_type` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'Description of available jobs in the game.';


-- -----------------------------------------------------
-- Table `projectfflogs`.`static`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `projectfflogs`.`static` (
  `id_static` INT(11) NOT NULL ,
  `static_name` VARCHAR(45) NOT NULL ,
  PRIMARY KEY (`id_static`) ,
  UNIQUE INDEX `id_static_UNIQUE` (`id_static` ASC) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'Information about a static (a party with 8 members doing raids).';


-- -----------------------------------------------------
-- Table `projectfflogs`.`report`
-- -----------------------------------------------------
-- *** Update : id_expansion deleted : too complex, not essential needs (anotherway can be find)
CREATE  TABLE IF NOT EXISTS `projectfflogs`.`report` (
  `id_report` VARCHAR(255) NOT NULL ,
  `report_date` DATETIME NOT NULL ,
  `fk_owner` INT(11) NOT NULL ,
  `fk_id_static` INT(11) NULL DEFAULT NULL ,
  PRIMARY KEY (`id_report`) ,
  UNIQUE INDEX `id_report_UNIQUE` (`id_report` ASC) ,
  INDEX `fk_owner_idx` (`fk_owner` ASC) ,
  INDEX `fk_id_guild_idx` (`fk_id_static` ASC) ,
  CONSTRAINT `fk_id_static_report`
    FOREIGN KEY (`fk_id_static` )
    REFERENCES `projectfflogs`.`static` (`id_static` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_owner`
    FOREIGN KEY (`fk_owner` )
    REFERENCES `projectfflogs`.`user` (`id_user` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'Report per guild and/or owner.';


-- -----------------------------------------------------
-- Table `projectfflogs`.`staticmember`
-- -----------------------------------------------------
-- *** Update : fk_id_user delete and replaced by fk_id_character
CREATE  TABLE IF NOT EXISTS `projectfflogs`.`staticmember` (
  `fk_id_static` INT(11) NOT NULL ,
  `fk_id_character` INT(11) NOT NULL ,
  PRIMARY KEY (`fk_id_static`, `fk_id_character`) ,
  INDEX `fk_id_static_idx` (`fk_id_static` ASC) ,
  INDEX `fk_id_character_idx` (`fk_id_character` ASC) ,
  CONSTRAINT `fk_id_static`
    FOREIGN KEY (`fk_id_static` )
    REFERENCES `projectfflogs`.`static` (`id_static` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_id_character`
    FOREIGN KEY (`fk_id_character` )
    REFERENCES `projectfflogs`.`character` (`id_character` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'Information about member and static. One member can have several statics and one static has several members.';


-- -----------------------------------------------------
-- Table `projectfflogs`.`difficulty`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `projectfflogs`.`difficulty` (
  `id_difficulty` INT(11) NOT NULL ,
  `difficulty_name` VARCHAR(255) NOT NULL ,
  PRIMARY KEY (`id_difficulty`) ,
  UNIQUE INDEX `id_difficulty_UNIQUE` (`id_difficulty` ASC) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'Different kind of difficulty that FFXIV fights references to.';


-- -----------------------------------------------------
-- Table `projectfflogs`.`encounter`
-- -----------------------------------------------------
-- *** Update : fk_id_difficulty become a part of primary key, 
-- *** Update : fk_id_timeline become a string (before was an int) and refersto an encounter id + dicfficulty (format : 87-500) (to retrieve the good timeline)
-- *** Note : timeline differs between two different kind of difficulty for a fight/encounter
-- *** Note : timeline can be null if the fight/encounter is not supported
CREATE  TABLE IF NOT EXISTS `projectfflogs`.`encounter` (
  `id_encounter` INT(11) NOT NULL ,
  `fk_id_difficulty` INT(11) NOT NULL ,
  `encounter_name` VARCHAR(255) ,
  `boss_name` VARCHAR(255) ,  
  `fk_id_timeline` VARCHAR(255) NULL DEFAULT NULL ,
  PRIMARY KEY (`id_encounter`, `fk_id_difficulty`) ,
  INDEX `id_encounter` (`id_encounter` ASC) ,
  INDEX `fk_id_difficulty_idx` (`fk_id_difficulty` ASC) ,
  CONSTRAINT `fk_id_difficulty`
    FOREIGN KEY (`fk_id_difficulty` )
    REFERENCES `projectfflogs`.`difficulty` (`id_difficulty` )
    ON DELETE NO ACTION 
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'Information about a fight in FFXIV. The timeline id references an id of a timeline document in a collection of a MongoDB database.';


-- -----------------------------------------------------
-- Table `projectfflogs`.`try`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `projectfflogs`.`try` (
  `id_try` INT(11) NOT NULL ,
  `fk_id_report` VARCHAR(255) NOT NULL ,
  `fk_id_encounter` INT(11) NOT NULL ,
  `boss_percentage` DOUBLE NULL DEFAULT NULL ,
  `encounter_percentage` DOUBLE NULL DEFAULT NULL ,
  `is_clear` TINYINT(4) NOT NULL ,
  `start_time` INT(11) NULL DEFAULT NULL ,
  `end_time` INT(11) NULL DEFAULT NULL ,
  PRIMARY KEY (`id_try`, `fk_id_report`) ,
  INDEX `fk_id_report_idx` (`fk_id_report` ASC) ,
  INDEX `fk_id_encounter_idx` (`fk_id_encounter` ASC) ,
  CONSTRAINT `fk_id_encounter`
    FOREIGN KEY (`fk_id_encounter` )
    REFERENCES `projectfflogs`.`encounter` (`id_encounter` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_id_report`
    FOREIGN KEY (`fk_id_report` )
    REFERENCES `projectfflogs`.`report` (`id_report` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'All try on diffferent encounters for a report. ';


-- -----------------------------------------------------
-- Table `projectfflogs`.`teampertry`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `projectfflogs`.`teampertry` (
  `fk_id_try` INT(11) NOT NULL ,
  `fk_id_report` VARCHAR(255) NOT NULL ,
  `fk_id_character` INT(11) NOT NULL ,
  `fk_id_job` INT(11) NOT NULL ,
  PRIMARY KEY (`fk_id_try`, `fk_id_report`, `fk_id_character`, `fk_id_job`) ,
  INDEX `fk_id_try_idx` (`fk_id_try` ASC) ,
  INDEX `fk_id_report_idx` (`fk_id_report` ASC) ,
  INDEX `fk_id_character_idx` (`fk_id_character` ASC) ,
  INDEX `fk_id_job_idx` (`fk_id_job` ASC) ,
  CONSTRAINT `fk_id_character_teampertry`
    FOREIGN KEY (`fk_id_character` )
    REFERENCES `projectfflogs`.`character` (`id_character` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_id_job`
    FOREIGN KEY (`fk_id_job` )
    REFERENCES `projectfflogs`.`job` (`id_job` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_id_report_team`
    FOREIGN KEY (`fk_id_report` )
    REFERENCES `projectfflogs`.`report` (`id_report` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_id_try`
    FOREIGN KEY (`fk_id_try` )
    REFERENCES `projectfflogs`.`try` (`id_try` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'Reference to retrieve information to know for each try relative to report which character with wich job had participated.';

USE `projectfflogs` ;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
