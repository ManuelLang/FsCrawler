/*
 * Copyright (c) 2023. Manuel LANG
 * Software under GNU AGPLv3 licence
 */

-- Represents meaningful data contained into 1 or many files (logical way to group files that belong to same stuff)
CREATE TABLE IF NOT EXISTS `content`
(
    `id`              int(11)       NOT NULL,
    `name`       varchar(25)   NOT NULL,
    PRIMARY KEY (`id`),
    KEY `ix_content_id` (`id`)
);

CREATE TABLE IF NOT EXISTS `content_family`
(
    `id`              int(11)       NOT NULL,
    `name`       varchar(25)   NOT NULL,
    PRIMARY KEY (`id`),
    KEY `ix_content_family_id` (`id`)
);
INSERT INTO `content_family` (id, name) VALUES (1, 'AUDIO');
INSERT INTO `content_family` (id, name) VALUES (2, 'PICTURE');
INSERT INTO `content_family` (id, name) VALUES (3, 'VIDEO');
INSERT INTO `content_family` (id, name) VALUES (4, 'DOCUMENT');
INSERT INTO `content_family` (id, name) VALUES (5, 'APPLICATION');
INSERT INTO `content_family` (id, name) VALUES (6, 'ARCHIVE');

CREATE TABLE IF NOT EXISTS `content_category`
(
    `id`              int(11)       NOT NULL,
    `name`       varchar(25)   NOT NULL,
    PRIMARY KEY (`id`),
    KEY `ix_content_category_id` (`id`)
);
INSERT INTO `content_category` (id, name) VALUES (1, 'MUSIC');
INSERT INTO `content_category` (id, name) VALUES (2, 'BOOK');
INSERT INTO `content_category` (id, name) VALUES (3, 'MOVIE');
INSERT INTO `content_category` (id, name) VALUES (4, 'ANIME');
INSERT INTO `content_category` (id, name) VALUES (5, 'SERIES');
INSERT INTO `content_category` (id, name) VALUES (6, 'PHOTO');
INSERT INTO `content_category` (id, name) VALUES (7, 'PAPER');
INSERT INTO `content_category` (id, name) VALUES (8, 'CODE');
INSERT INTO `content_category` (id, name) VALUES (9, 'ADULT');
INSERT INTO `content_category` (id, name) VALUES (10, 'GAME');
INSERT INTO `content_category` (id, name) VALUES (11, 'APP');

CREATE TABLE IF NOT EXISTS `rating`
(
    `id`              int(11)       NOT NULL,
    `name`       varchar(25)   NOT NULL,
    PRIMARY KEY (`id`),
    KEY `ix_rating_id` (`id`)
);
INSERT INTO `rating` (id, name) VALUES (1, 'BAD');
INSERT INTO `rating` (id, name) VALUES (2, 'POOR');
INSERT INTO `rating` (id, name) VALUES (3, 'AVERAGE');
INSERT INTO `rating` (id, name) VALUES (4, 'GREAT');
INSERT INTO `rating` (id, name) VALUES (5, 'EXCELLENT');

CREATE TABLE IF NOT EXISTS `content_classification_pegi_age`
(
    `id`              int(11)       NOT NULL,
    `name`       varchar(25)   NOT NULL,
    PRIMARY KEY (`id`),
    KEY `ix_content_classification_pegi_age_id` (`id`)
);
INSERT INTO `content_classification_pegi_age` (id, name) VALUES (1, 3);
INSERT INTO `content_classification_pegi_age` (id, name) VALUES (2, 7);
INSERT INTO `content_classification_pegi_age` (id, name) VALUES (3, 12);
INSERT INTO `content_classification_pegi_age` (id, name) VALUES (4, 16);
INSERT INTO `content_classification_pegi_age` (id, name) VALUES (5, 18);

CREATE TABLE IF NOT EXISTS `tags`
(
    `id`              int(11)       NOT NULL,
    `name`       varchar(25)        NOT NULL,
    `color`       varchar(25)       NULL,
    PRIMARY KEY (`id`),
    KEY `ix_tags_id` (`id`)
);
INSERT INTO `tags` (id, name) VALUES (1, 'A faire');
INSERT INTO `tags` (id, name) VALUES (2, 'Confidentiel');
INSERT INTO `tags` (id, name) VALUES (3, 'Travail');
INSERT INTO `tags` (id, name) VALUES (4, 'Vu');
INSERT INTO `tags` (id, name) VALUES (5, 'Justificatif');

CREATE TABLE IF NOT EXISTS `path_type`
(
    `id`              int(11)       NOT NULL,
    `name`       varchar(25)   NOT NULL,
    PRIMARY KEY (`id`),
    KEY `ix_path_type_id` (`id`)
);
INSERT INTO `path_type` (id, name) VALUES (1, 'FILE');
INSERT INTO `path_type` (id, name) VALUES (2, 'DIRECTORY');

CREATE TABLE IF NOT EXISTS `path_stage`
(
    `id`              int(11)       NOT NULL,
    `name`       varchar(25)   NOT NULL,
    PRIMARY KEY (`id`),
    KEY `ix_path_stage_id` (`id`)
);
INSERT INTO `path_stage` (id, name) VALUES (1, 'CRAWLED');
INSERT INTO `path_stage` (id, name) VALUES (2, 'ATTRIBUTES_EXTRACTED');
INSERT INTO `path_stage` (id, name) VALUES (3, 'HASH_COMPUTED');
INSERT INTO `path_stage` (id, name) VALUES (4, 'TEXT_EXTRACTED');
INSERT INTO `path_stage` (id, name) VALUES (5, 'THUMBNAIL_GENERATED');
INSERT INTO `path_stage` (id, name) VALUES (6, 'INDEXED');
INSERT INTO `path_stage` (id, name) VALUES (7, 'PATH_DELETED');


CREATE TABLE IF NOT EXISTS `path`
(
    `id`              int(11)       NOT NULL AUTO_INCREMENT,
    `path`            varchar(2000) NOT NULL,
    `extension`       varchar(25)   DEFAULT NULL,
    `name`            varchar(2000) NOT NULL,
    `owner`           varchar(255)           DEFAULT NULL,
    `group`           varchar(255)           DEFAULT NULL,
    `root`            varchar(255)           DEFAULT NULL,
    `drive`           varchar(25)            DEFAULT NULL,
    `size`      BIGINT                 DEFAULT NULL,
    `hash`            char(64)               DEFAULT NULL,
    `is_windows_path` binary(1)              DEFAULT NULL,
    `hidden`          binary(1)              DEFAULT NULL,
    `archive`         binary(1)              DEFAULT NULL,
    `compressed`      binary(1)              DEFAULT NULL,
    `encrypted`       binary(1)              DEFAULT NULL,
    `offline`         binary(1)              DEFAULT NULL,
    `readonly`        binary(1)              DEFAULT NULL,
    `system`          binary(1)              DEFAULT NULL,
    `temporary`       binary(1)              DEFAULT NULL,
    `content_family`  int(11)                DEFAULT NULL,
    `content_category`  int(11)                DEFAULT NULL,
    `content_rating`  int(11)                DEFAULT NULL,
    `content_min_age`  int(11)                DEFAULT NULL,
    `quality_rating`  int(11)                DEFAULT NULL,
    `mime_type`       varchar(255)           DEFAULT NULL,
    `path_type`       int(11)                DEFAULT NULL,
    `files_in_dir`    int(11)                DEFAULT NULL,
    `path_stage`      int(11)                DEFAULT NULL,
    `tags`            varchar(2000)          DEFAULT NULL,
    `date_created`    timestamp     NOT NULL DEFAULT current_timestamp(),
    `date_updated`    timestamp     NOT NULL DEFAULT current_timestamp(),
    PRIMARY KEY (`id`),
    KEY `ix_path_id` (`id`),
    KEY `ix_path_path` (`path`),
    KEY `ix_path_name` (`name`),
    KEY `ix_path_ext` (`extension`),
    KEY `ix_path_drive` (`drive`),
    KEY `ix_path_size` (`size`),
    KEY `ix_path_hash` (`hash`),
    KEY `ix_path_content` (`content_family`),
    KEY `ix_path_type` (`path_type`),
    KEY `ix_path_stage` (`path_stage`),
    KEY `ix_path_updated` (`date_updated`),
    CONSTRAINT `uk_path` UNIQUE (`path`),
    CONSTRAINT `fk_path_type` FOREIGN KEY (path_type) REFERENCES path_type(id),
    CONSTRAINT `fk_path_stage` FOREIGN KEY (path_stage) REFERENCES path_stage(id),
    CONSTRAINT `fk_content_family` FOREIGN KEY (content_family) REFERENCES content_family(id),
    CONSTRAINT `fk_content_category` FOREIGN KEY (content_category) REFERENCES content_category(id),
    CONSTRAINT `fk_content_rating` FOREIGN KEY (content_rating) REFERENCES rating(id),
    CONSTRAINT `fk_quality_rating` FOREIGN KEY (quality_rating) REFERENCES rating(id),
    CONSTRAINT `fk_content_min_age` FOREIGN KEY (content_min_age) REFERENCES content_classification_pegi_age(id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_bin;


CREATE TABLE IF NOT EXISTS `content_tags`
(
    `path_id`                int(11)       NOT NULL,
    `tag_id`                 int(11)       NOT NULL,
    PRIMARY KEY (`path_id`, `tag_id`),
    KEY `ix_content_tags_id` (`path_id`, `tag_id`),
    CONSTRAINT `fk_content_tags_tags` FOREIGN KEY (tag_id) REFERENCES tags(id),
    CONSTRAINT `fk_content_tags_path` FOREIGN KEY (path_id) REFERENCES path(id)
);

CREATE TABLE IF NOT EXISTS `content_files`
(
    `content_id`              int(11)       NOT NULL,
    `path_id`                 int(11)       NOT NULL,
    PRIMARY KEY (`content_id`, `path_id`),
    KEY `ix_content_files_id` (`content_id`, `path_id`),
    CONSTRAINT `fk_content_files_content` FOREIGN KEY (content_id) REFERENCES content(id),
    CONSTRAINT `fk_content_files_path` FOREIGN KEY (path_id) REFERENCES path(id)
);
