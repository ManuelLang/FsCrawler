/*
 * Copyright (c) 2023. Manuel LANG
 * Software under GNU AGPLv3 licence
 */

CREATE TABLE IF NOT EXISTS `path`
(
    `id`              int(11)       NOT NULL AUTO_INCREMENT,
    `path`            varchar(2000) NOT NULL UNIQUE,
    `extension`       varchar(32)   NOT NULL,
    `name`            varchar(2000) NOT NULL,
    `owner`           varchar(255)           DEFAULT NULL,
    `group`           varchar(255)           DEFAULT NULL,
    `root`            varchar(255)           DEFAULT NULL,
    `drive`           varchar(25)            DEFAULT NULL,
    `size_in_mb`      DECIMAL(20, 12)        DEFAULT NULL,
    `hash_md5`        char(32)               DEFAULT NULL,
    `hash_sha256`     char(64)               DEFAULT NULL,
    `is_windows_path` binary(1)              DEFAULT NULL,
    `hidden`          binary(1)              DEFAULT NULL,
    `archive`         binary(1)              DEFAULT NULL,
    `compressed`      binary(1)              DEFAULT NULL,
    `encrypted`       binary(1)              DEFAULT NULL,
    `offline`         binary(1)              DEFAULT NULL,
    `readonly`        binary(1)              DEFAULT NULL,
    `system`          binary(1)              DEFAULT NULL,
    `temporary`       binary(1)              DEFAULT NULL,
    `content_family`  varchar(25)            DEFAULT NULL,
    `mime_type`       varchar(255)           DEFAULT NULL,
    `path_type`       varchar(25)            DEFAULT NULL,
    `files_in_dir`    int(11)                DEFAULT NULL,
    `path_stage`      varchar(25)            DEFAULT NULL,
    `tags`            varchar(2000)          DEFAULT NULL,
    `date_created`    timestamp     NOT NULL DEFAULT current_timestamp(),
    `date_updated`    timestamp     NOT NULL DEFAULT current_timestamp(),
    PRIMARY KEY (`id`),
    KEY `ix_path_id` (`id`),
    KEY `ix_path_path` (`path`),
    KEY `ix_path_name` (`name`),
    KEY `ix_path_ext` (`extension`),
    KEY `ix_path_drive` (`drive`),
    KEY `ix_path_size` (`size_in_mb`),
    KEY `ix_path_hash_md5` (`hash_md5`),
    KEY `ix_path_hash_sha256` (`hash_sha256`),
    KEY `ix_path_content` (`content_family`),
    KEY `ix_path_type` (`path_type`),
    KEY `ix_path_stage` (`path_stage`),
    KEY `ix_path_updated` (`date_updated`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
