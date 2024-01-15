/*
 * Copyright (c) 2023. Manuel LANG
 * Software under GNU AGPLv3 licence
 */

-- Represents meaningful data contained into 1 or many files (logical way to group files that belong to same stuff)
CREATE TABLE IF NOT EXISTS content
(
    id              int       NOT NULL,
    name       varchar(25)   NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS content_family
(
    id              int       NOT NULL,
    name       varchar(25)   NOT NULL,
    PRIMARY KEY (id)
);
INSERT INTO content_family (id, name) VALUES (1, 'AUDIO');
INSERT INTO content_family (id, name) VALUES (2, 'PICTURE');
INSERT INTO content_family (id, name) VALUES (3, 'VIDEO');
INSERT INTO content_family (id, name) VALUES (4, 'DOCUMENT');
INSERT INTO content_family (id, name) VALUES (5, 'APPLICATION');
INSERT INTO content_family (id, name) VALUES (6, 'ARCHIVE');

CREATE TABLE IF NOT EXISTS content_category
(
    id              int       NOT NULL,
    name       varchar(25)   NOT NULL,
    PRIMARY KEY (id)
);
INSERT INTO content_category (id, name) VALUES (1, 'MUSIC');
INSERT INTO content_category (id, name) VALUES (2, 'BOOK');
INSERT INTO content_category (id, name) VALUES (3, 'MOVIE');
INSERT INTO content_category (id, name) VALUES (4, 'ANIME');
INSERT INTO content_category (id, name) VALUES (5, 'SERIES');
INSERT INTO content_category (id, name) VALUES (6, 'PHOTO');
INSERT INTO content_category (id, name) VALUES (7, 'PAPER');
INSERT INTO content_category (id, name) VALUES (8, 'CODE');
INSERT INTO content_category (id, name) VALUES (9, 'ADULT');
INSERT INTO content_category (id, name) VALUES (10, 'GAME');

CREATE TABLE IF NOT EXISTS rating
(
    id              int       NOT NULL,
    name       varchar(25)   NOT NULL,
    PRIMARY KEY (id)
);
INSERT INTO rating (id, name) VALUES (1, 'BAD');
INSERT INTO rating (id, name) VALUES (2, 'POOR');
INSERT INTO rating (id, name) VALUES (3, 'AVERAGE');
INSERT INTO rating (id, name) VALUES (4, 'GREAT');
INSERT INTO rating (id, name) VALUES (5, 'EXCELLENT');

CREATE TABLE IF NOT EXISTS content_classification_pegi_age
(
    id              int       NOT NULL,
    name       varchar(25)   NOT NULL,
    PRIMARY KEY (id)
);
INSERT INTO content_classification_pegi_age (id, name) VALUES (1, 3);
INSERT INTO content_classification_pegi_age (id, name) VALUES (2, 7);
INSERT INTO content_classification_pegi_age (id, name) VALUES (3, 12);
INSERT INTO content_classification_pegi_age (id, name) VALUES (4, 16);
INSERT INTO content_classification_pegi_age (id, name) VALUES (5, 18);

CREATE TABLE IF NOT EXISTS tags
(
    id              int       NOT NULL,
    name       varchar(25)        NOT NULL,
    color       varchar(25)       NULL,
    PRIMARY KEY (id)
);
INSERT INTO tags (id, name) VALUES (1, 'A faire');
INSERT INTO tags (id, name) VALUES (2, 'Confidentiel');
INSERT INTO tags (id, name) VALUES (3, 'Travail');
INSERT INTO tags (id, name) VALUES (4, 'Vu');
INSERT INTO tags (id, name) VALUES (5, 'Justificatif');

CREATE TABLE IF NOT EXISTS path_type
(
    id              int       NOT NULL,
    name       varchar(25)   NOT NULL,
    PRIMARY KEY (id)
);
INSERT INTO path_type (id, name) VALUES (1, 'FILE');
INSERT INTO path_type (id, name) VALUES (2, 'DIRECTORY');

CREATE TABLE IF NOT EXISTS path_stage
(
    id              int       NOT NULL,
    name       varchar(25)   NOT NULL,
    PRIMARY KEY (id)
);
INSERT INTO path_stage (id, name) VALUES (1, 'CRAWLED');
INSERT INTO path_stage (id, name) VALUES (2, 'ATTRIBUTES_EXTRACTED');
INSERT INTO path_stage (id, name) VALUES (3, 'HASH_COMPUTED');
INSERT INTO path_stage (id, name) VALUES (4, 'TEXT_EXTRACTED');
INSERT INTO path_stage (id, name) VALUES (5, 'THUMBNAIL_GENERATED');
INSERT INTO path_stage (id, name) VALUES (6, 'INDEXED');
INSERT INTO path_stage (id, name) VALUES (7, 'PATH_DELETED');


create table if not exists path_apps
(
    id SERIAL primary key,
    path varchar(2000) not null,
    extension varchar(25) default null,
    name varchar(2000) not null,
    owner varchar(255) default null,
    "group" varchar(255) default null,
    root varchar(255) default null,
    drive varchar(25) default null,
    size BIGINT default null,
    hash char(64) default null,
    is_windows_path boolean default null,
    hidden boolean default null,
    archive boolean default null,
    compressed boolean default null,
    encrypted boolean default null,
    offline boolean default null,
    readonly boolean default null,
    system boolean default null,
    temporary boolean default null,
    content_family int default null,
    content_category int default null,
    content_rating int default null,
    content_min_age int default null,
    quality_rating int default null,
    mime_type varchar(255) default null,
    path_type int default null,
    files_in_dir int default null,
    path_stage int default null,
    tags varchar(2000) default null,
    date_created timestamp not null default now(),
    date_updated timestamp not null default now(),
    constraint uk_path_apps unique (path),
    constraint fk_path_type_apps foreign key (path_type) references path_type(id),
    constraint fk_path_stage_apps foreign key (path_stage) references path_stage(id),
    constraint fk_content_family_apps foreign key (content_family) references content_family(id),
    constraint fk_content_category_apps foreign key (content_category) references content_category(id),
    constraint fk_content_rating_apps foreign key (content_rating) references rating(id),
    constraint fk_quality_rating_apps foreign key (quality_rating) references rating(id),
    constraint fk_content_min_age_apps foreign key (content_min_age) references content_classification_pegi_age(id)
);
CREATE UNIQUE INDEX ix_path_path_apps ON path_apps (path);
CREATE INDEX ix_path_name_apps ON path_apps (name);
CREATE INDEX ix_path_ext_apps ON path_apps (extension);
CREATE INDEX ix_path_drive_apps ON path_apps (drive);
CREATE INDEX ix_path_size_apps ON path_apps (size);
CREATE INDEX ix_path_hash_apps ON path_apps (hash);
CREATE INDEX ix_path_content_apps ON path_apps (content_family);
CREATE INDEX ix_path_type_apps ON path_apps (path_type);
CREATE INDEX ix_path_stage_apps ON path_apps (path_stage);
CREATE INDEX ix_path_updated_apps ON path_apps (date_updated);


create table if not exists path_atrier
(
    id SERIAL primary key,
    path varchar(2000) not null,
    extension varchar(25) default null,
    name varchar(2000) not null,
    owner varchar(255) default null,
    "group" varchar(255) default null,
    root varchar(255) default null,
    drive varchar(25) default null,
    size BIGINT default null,
    hash char(64) default null,
    is_windows_path boolean default null,
    hidden boolean default null,
    archive boolean default null,
    compressed boolean default null,
    encrypted boolean default null,
    offline boolean default null,
    readonly boolean default null,
    system boolean default null,
    temporary boolean default null,
    content_family int default null,
    content_category int default null,
    content_rating int default null,
    content_min_age int default null,
    quality_rating int default null,
    mime_type varchar(255) default null,
    path_type int default null,
    files_in_dir int default null,
    path_stage int default null,
    tags varchar(2000) default null,
    date_created timestamp not null default now(),
    date_updated timestamp not null default now(),
    constraint uk_path_atrier unique (path),
    constraint fk_path_type_atrier foreign key (path_type) references path_type(id),
    constraint fk_path_stage_atrier foreign key (path_stage) references path_stage(id),
    constraint fk_content_family_atrier foreign key (content_family) references content_family(id),
    constraint fk_content_category_atrier foreign key (content_category) references content_category(id),
    constraint fk_content_rating_atrier foreign key (content_rating) references rating(id),
    constraint fk_quality_rating_atrier foreign key (quality_rating) references rating(id),
    constraint fk_content_min_age_atrier foreign key (content_min_age) references content_classification_pegi_age(id)
);
CREATE UNIQUE INDEX ix_path_path_atrier ON path_atrier (path);
CREATE INDEX ix_path_name_atrier ON path_atrier (name);
CREATE INDEX ix_path_ext_atrier ON path_atrier (extension);
CREATE INDEX ix_path_drive_atrier ON path_atrier (drive);
CREATE INDEX ix_path_size_atrier ON path_atrier (size);
CREATE INDEX ix_path_hash_atrier ON path_atrier (hash);
CREATE INDEX ix_path_content_atrier ON path_atrier (content_family);
CREATE INDEX ix_path_type_atrier ON path_atrier (path_type);
CREATE INDEX ix_path_stage_atrier ON path_atrier (path_stage);
CREATE INDEX ix_path_updated_atrier ON path_atrier (date_updated);


create table if not exists path_backups
(
    id SERIAL primary key,
    path varchar(2000) not null,
    extension varchar(25) default null,
    name varchar(2000) not null,
    owner varchar(255) default null,
    "group" varchar(255) default null,
    root varchar(255) default null,
    drive varchar(25) default null,
    size BIGINT default null,
    hash char(64) default null,
    is_windows_path boolean default null,
    hidden boolean default null,
    archive boolean default null,
    compressed boolean default null,
    encrypted boolean default null,
    offline boolean default null,
    readonly boolean default null,
    system boolean default null,
    temporary boolean default null,
    content_family int default null,
    content_category int default null,
    content_rating int default null,
    content_min_age int default null,
    quality_rating int default null,
    mime_type varchar(255) default null,
    path_type int default null,
    files_in_dir int default null,
    path_stage int default null,
    tags varchar(2000) default null,
    date_created timestamp not null default now(),
    date_updated timestamp not null default now(),
    constraint uk_path_backups unique (path),
    constraint fk_path_type_backups foreign key (path_type) references path_type(id),
    constraint fk_path_stage_backups foreign key (path_stage) references path_stage(id),
    constraint fk_content_family_backups foreign key (content_family) references content_family(id),
    constraint fk_content_category_backups foreign key (content_category) references content_category(id),
    constraint fk_content_rating_backups foreign key (content_rating) references rating(id),
    constraint fk_quality_rating_backups foreign key (quality_rating) references rating(id),
    constraint fk_content_min_age_backups foreign key (content_min_age) references content_classification_pegi_age(id)
);
CREATE UNIQUE INDEX ix_path_path_backups ON path_backups (path);
CREATE INDEX ix_path_name_backups ON path_backups (name);
CREATE INDEX ix_path_ext_backups ON path_backups(extension);
CREATE INDEX ix_path_drive_backups ON path_backups (drive);
CREATE INDEX ix_path_size_backups ON path_backups (size);
CREATE INDEX ix_path_hash_backups ON path_backups (hash);
CREATE INDEX ix_path_content_backups ON path_backups (content_family);
CREATE INDEX ix_path_type_backups ON path_backups (path_type);
CREATE INDEX ix_path_stage_backups ON path_backups (path_stage);
CREATE INDEX ix_path_updated_backups ON path_backups (date_updated);


create table if not exists path_developpement
(
    id SERIAL primary key,
    path varchar(2000) not null,
    extension varchar(25) default null,
    name varchar(2000) not null,
    owner varchar(255) default null,
    "group" varchar(255) default null,
    root varchar(255) default null,
    drive varchar(25) default null,
    size BIGINT default null,
    hash char(64) default null,
    is_windows_path boolean default null,
    hidden boolean default null,
    archive boolean default null,
    compressed boolean default null,
    encrypted boolean default null,
    offline boolean default null,
    readonly boolean default null,
    system boolean default null,
    temporary boolean default null,
    content_family int default null,
    content_category int default null,
    content_rating int default null,
    content_min_age int default null,
    quality_rating int default null,
    mime_type varchar(255) default null,
    path_type int default null,
    files_in_dir int default null,
    path_stage int default null,
    tags varchar(2000) default null,
    date_created timestamp not null default now(),
    date_updated timestamp not null default now(),
    constraint uk_path_developpement unique (path),
    constraint fk_path_type_developpement foreign key (path_type) references path_type(id),
    constraint fk_path_stage_developpement foreign key (path_stage) references path_stage(id),
    constraint fk_content_family_developpement foreign key (content_family) references content_family(id),
    constraint fk_content_category_developpement foreign key (content_category) references content_category(id),
    constraint fk_content_rating_developpement foreign key (content_rating) references rating(id),
    constraint fk_quality_rating_developpement foreign key (quality_rating) references rating(id),
    constraint fk_content_min_age_developpement foreign key (content_min_age) references content_classification_pegi_age(id)
);
CREATE UNIQUE INDEX ix_path_path_developpement ON path_developpement (path);
CREATE INDEX ix_path_name_developpement ON path_developpement (name);
CREATE INDEX ix_path_ext_developpement ON path_developpement(extension);
CREATE INDEX ix_path_drive_developpement ON path_developpement (drive);
CREATE INDEX ix_path_size_developpement ON path_developpement (size);
CREATE INDEX ix_path_hash_developpement ON path_developpement (hash);
CREATE INDEX ix_path_content_developpement ON path_developpement (content_family);
CREATE INDEX ix_path_type_developpement ON path_developpement (path_type);
CREATE INDEX ix_path_stage_developpement ON path_developpement (path_stage);
CREATE INDEX ix_path_updated_developpement ON path_developpement (date_updated);


create table if not exists path_documents
(
    id SERIAL primary key,
    path varchar(2000) not null,
    extension varchar(25) default null,
    name varchar(2000) not null,
    owner varchar(255) default null,
    "group" varchar(255) default null,
    root varchar(255) default null,
    drive varchar(25) default null,
    size BIGINT default null,
    hash char(64) default null,
    is_windows_path boolean default null,
    hidden boolean default null,
    archive boolean default null,
    compressed boolean default null,
    encrypted boolean default null,
    offline boolean default null,
    readonly boolean default null,
    system boolean default null,
    temporary boolean default null,
    content_family int default null,
    content_category int default null,
    content_rating int default null,
    content_min_age int default null,
    quality_rating int default null,
    mime_type varchar(255) default null,
    path_type int default null,
    files_in_dir int default null,
    path_stage int default null,
    tags varchar(2000) default null,
    date_created timestamp not null default now(),
    date_updated timestamp not null default now(),
    constraint uk_path_documents unique (path),
    constraint fk_path_type_documents foreign key (path_type) references path_type(id),
    constraint fk_path_stage_documents foreign key (path_stage) references path_stage(id),
    constraint fk_content_family_documents foreign key (content_family) references content_family(id),
    constraint fk_content_category_documents foreign key (content_category) references content_category(id),
    constraint fk_content_rating_documents foreign key (content_rating) references rating(id),
    constraint fk_quality_rating_documents foreign key (quality_rating) references rating(id),
    constraint fk_content_min_age_documents foreign key (content_min_age) references content_classification_pegi_age(id)
);
CREATE UNIQUE INDEX ix_path_path_documents ON path_documents (path);
CREATE INDEX ix_path_name_documents ON path_documents (name);
CREATE INDEX ix_path_ext_documents ON path_documents(extension);
CREATE INDEX ix_path_drive_documents ON path_documents (drive);
CREATE INDEX ix_path_size_documents ON path_documents (size);
CREATE INDEX ix_path_hash_documents ON path_documents (hash);
CREATE INDEX ix_path_content_documents ON path_documents (content_family);
CREATE INDEX ix_path_type_documents ON path_documents (path_type);
CREATE INDEX ix_path_stage_documents ON path_documents (path_stage);
CREATE INDEX ix_path_updated_documents ON path_documents (date_updated);


create table if not exists path_homes
(
    id SERIAL primary key,
    path varchar(2000) not null,
    extension varchar(25) default null,
    name varchar(2000) not null,
    owner varchar(255) default null,
    "group" varchar(255) default null,
    root varchar(255) default null,
    drive varchar(25) default null,
    size BIGINT default null,
    hash char(64) default null,
    is_windows_path boolean default null,
    hidden boolean default null,
    archive boolean default null,
    compressed boolean default null,
    encrypted boolean default null,
    offline boolean default null,
    readonly boolean default null,
    system boolean default null,
    temporary boolean default null,
    content_family int default null,
    content_category int default null,
    content_rating int default null,
    content_min_age int default null,
    quality_rating int default null,
    mime_type varchar(255) default null,
    path_type int default null,
    files_in_dir int default null,
    path_stage int default null,
    tags varchar(2000) default null,
    date_created timestamp not null default now(),
    date_updated timestamp not null default now(),
    constraint uk_path_homes unique (path),
    constraint fk_path_type_homes foreign key (path_type) references path_type(id),
    constraint fk_path_stage_homes foreign key (path_stage) references path_stage(id),
    constraint fk_content_family_homes foreign key (content_family) references content_family(id),
    constraint fk_content_category_homes foreign key (content_category) references content_category(id),
    constraint fk_content_rating_homes foreign key (content_rating) references rating(id),
    constraint fk_quality_rating_homes foreign key (quality_rating) references rating(id),
    constraint fk_content_min_age_homes foreign key (content_min_age) references content_classification_pegi_age(id)
);
CREATE UNIQUE INDEX ix_path_path_homes ON path_homes (path);
CREATE INDEX ix_path_name_homes ON path_homes (name);
CREATE INDEX ix_path_ext_homes ON path_homes(extension);
CREATE INDEX ix_path_drive_homes ON path_homes (drive);
CREATE INDEX ix_path_size_homes ON path_homes (size);
CREATE INDEX ix_path_hash_homes ON path_homes (hash);
CREATE INDEX ix_path_content_homes ON path_homes (content_family);
CREATE INDEX ix_path_type_homes ON path_homes (path_type);
CREATE INDEX ix_path_stage_homes ON path_homes (path_stage);
CREATE INDEX ix_path_updated_homes ON path_homes (date_updated);


create table if not exists path_jeux
(
    id SERIAL primary key,
    path varchar(2000) not null,
    extension varchar(25) default null,
    name varchar(2000) not null,
    owner varchar(255) default null,
    "group" varchar(255) default null,
    root varchar(255) default null,
    drive varchar(25) default null,
    size BIGINT default null,
    hash char(64) default null,
    is_windows_path boolean default null,
    hidden boolean default null,
    archive boolean default null,
    compressed boolean default null,
    encrypted boolean default null,
    offline boolean default null,
    readonly boolean default null,
    system boolean default null,
    temporary boolean default null,
    content_family int default null,
    content_category int default null,
    content_rating int default null,
    content_min_age int default null,
    quality_rating int default null,
    mime_type varchar(255) default null,
    path_type int default null,
    files_in_dir int default null,
    path_stage int default null,
    tags varchar(2000) default null,
    date_created timestamp not null default now(),
    date_updated timestamp not null default now(),
    constraint uk_path_jeux unique (path),
    constraint fk_path_type_jeux foreign key (path_type) references path_type(id),
    constraint fk_path_stage_jeux foreign key (path_stage) references path_stage(id),
    constraint fk_content_family_jeux foreign key (content_family) references content_family(id),
    constraint fk_content_category_jeux foreign key (content_category) references content_category(id),
    constraint fk_content_rating_jeux foreign key (content_rating) references rating(id),
    constraint fk_quality_rating_jeux foreign key (quality_rating) references rating(id),
    constraint fk_content_min_age_jeux foreign key (content_min_age) references content_classification_pegi_age(id)
);
CREATE UNIQUE INDEX ix_path_path_jeux ON path_jeux (path);
CREATE INDEX ix_path_name_jeux ON path_jeux (name);
CREATE INDEX ix_path_ext_jeux ON path_jeux(extension);
CREATE INDEX ix_path_drive_jeux ON path_jeux (drive);
CREATE INDEX ix_path_size_jeux ON path_jeux (size);
CREATE INDEX ix_path_hash_jeux ON path_jeux (hash);
CREATE INDEX ix_path_content_jeux ON path_jeux (content_family);
CREATE INDEX ix_path_type_jeux ON path_jeux (path_type);
CREATE INDEX ix_path_stage_jeux ON path_jeux (path_stage);
CREATE INDEX ix_path_updated_jeux ON path_jeux (date_updated);


create table if not exists path_media
(
    id SERIAL primary key,
    path varchar(2000) not null,
    extension varchar(25) default null,
    name varchar(2000) not null,
    owner varchar(255) default null,
    "group" varchar(255) default null,
    root varchar(255) default null,
    drive varchar(25) default null,
    size BIGINT default null,
    hash char(64) default null,
    is_windows_path boolean default null,
    hidden boolean default null,
    archive boolean default null,
    compressed boolean default null,
    encrypted boolean default null,
    offline boolean default null,
    readonly boolean default null,
    system boolean default null,
    temporary boolean default null,
    content_family int default null,
    content_category int default null,
    content_rating int default null,
    content_min_age int default null,
    quality_rating int default null,
    mime_type varchar(255) default null,
    path_type int default null,
    files_in_dir int default null,
    path_stage int default null,
    tags varchar(2000) default null,
    date_created timestamp not null default now(),
    date_updated timestamp not null default now(),
    constraint uk_path_media unique (path),
    constraint fk_path_type_media foreign key (path_type) references path_type(id),
    constraint fk_path_stage_media foreign key (path_stage) references path_stage(id),
    constraint fk_content_family_media foreign key (content_family) references content_family(id),
    constraint fk_content_category_media foreign key (content_category) references content_category(id),
    constraint fk_content_rating_media foreign key (content_rating) references rating(id),
    constraint fk_quality_rating_media foreign key (quality_rating) references rating(id),
    constraint fk_content_min_age_media foreign key (content_min_age) references content_classification_pegi_age(id)
);
CREATE UNIQUE INDEX ix_path_path_media ON path_media (path);
CREATE INDEX ix_path_name_media ON path_media (name);
CREATE INDEX ix_path_ext_media ON path_media(extension);
CREATE INDEX ix_path_drive_media ON path_media (drive);
CREATE INDEX ix_path_size_media ON path_media (size);
CREATE INDEX ix_path_hash_media ON path_media (hash);
CREATE INDEX ix_path_content_media ON path_media (content_family);
CREATE INDEX ix_path_type_media ON path_media (path_type);
CREATE INDEX ix_path_stage_media ON path_media (path_stage);
CREATE INDEX ix_path_updated_media ON path_media (date_updated);


create table if not exists path_musique
(
    id SERIAL primary key,
    path varchar(2000) not null,
    extension varchar(25) default null,
    name varchar(2000) not null,
    owner varchar(255) default null,
    "group" varchar(255) default null,
    root varchar(255) default null,
    drive varchar(25) default null,
    size BIGINT default null,
    hash char(64) default null,
    is_windows_path boolean default null,
    hidden boolean default null,
    archive boolean default null,
    compressed boolean default null,
    encrypted boolean default null,
    offline boolean default null,
    readonly boolean default null,
    system boolean default null,
    temporary boolean default null,
    content_family int default null,
    content_category int default null,
    content_rating int default null,
    content_min_age int default null,
    quality_rating int default null,
    mime_type varchar(255) default null,
    path_type int default null,
    files_in_dir int default null,
    path_stage int default null,
    tags varchar(2000) default null,
    date_created timestamp not null default now(),
    date_updated timestamp not null default now(),
    constraint uk_path_musique unique (path),
    constraint fk_path_type_musique foreign key (path_type) references path_type(id),
    constraint fk_path_stage_musique foreign key (path_stage) references path_stage(id),
    constraint fk_content_family_musique foreign key (content_family) references content_family(id),
    constraint fk_content_category_musique foreign key (content_category) references content_category(id),
    constraint fk_content_rating_musique foreign key (content_rating) references rating(id),
    constraint fk_quality_rating_musique foreign key (quality_rating) references rating(id),
    constraint fk_content_min_age_musique foreign key (content_min_age) references content_classification_pegi_age(id)
);
CREATE UNIQUE INDEX ix_path_path_musique ON path_musique (path);
CREATE INDEX ix_path_name_musique ON path_musique (name);
CREATE INDEX ix_path_ext_musique ON path_musique(extension);
CREATE INDEX ix_path_drive_musique ON path_musique (drive);
CREATE INDEX ix_path_size_musique ON path_musique (size);
CREATE INDEX ix_path_hash_musique ON path_musique (hash);
CREATE INDEX ix_path_content_musique ON path_musique (content_family);
CREATE INDEX ix_path_type_musique ON path_musique (path_type);
CREATE INDEX ix_path_stage_musique ON path_musique (path_stage);
CREATE INDEX ix_path_updated_musique ON path_musique (date_updated);


create table if not exists path_photos
(
    id SERIAL primary key,
    path varchar(2000) not null,
    extension varchar(25) default null,
    name varchar(2000) not null,
    owner varchar(255) default null,
    "group" varchar(255) default null,
    root varchar(255) default null,
    drive varchar(25) default null,
    size BIGINT default null,
    hash char(64) default null,
    is_windows_path boolean default null,
    hidden boolean default null,
    archive boolean default null,
    compressed boolean default null,
    encrypted boolean default null,
    offline boolean default null,
    readonly boolean default null,
    system boolean default null,
    temporary boolean default null,
    content_family int default null,
    content_category int default null,
    content_rating int default null,
    content_min_age int default null,
    quality_rating int default null,
    mime_type varchar(255) default null,
    path_type int default null,
    files_in_dir int default null,
    path_stage int default null,
    tags varchar(2000) default null,
    date_created timestamp not null default now(),
    date_updated timestamp not null default now(),
    constraint uk_path_photos unique (path),
    constraint fk_path_type_photos foreign key (path_type) references path_type(id),
    constraint fk_path_stage_photos foreign key (path_stage) references path_stage(id),
    constraint fk_content_family_photos foreign key (content_family) references content_family(id),
    constraint fk_content_category_photos foreign key (content_category) references content_category(id),
    constraint fk_content_rating_photos foreign key (content_rating) references rating(id),
    constraint fk_quality_rating_photos foreign key (quality_rating) references rating(id),
    constraint fk_content_min_age_photos foreign key (content_min_age) references content_classification_pegi_age(id)
);
CREATE UNIQUE INDEX ix_path_path_photos ON path_photos (path);
CREATE INDEX ix_path_name_photos ON path_photos (name);
CREATE INDEX ix_path_ext_photos ON path_photos(extension);
CREATE INDEX ix_path_drive_photos ON path_photos (drive);
CREATE INDEX ix_path_size_photos ON path_photos (size);
CREATE INDEX ix_path_hash_photos ON path_photos (hash);
CREATE INDEX ix_path_content_photos ON path_photos (content_family);
CREATE INDEX ix_path_type_photos ON path_photos (path_type);
CREATE INDEX ix_path_stage_photos ON path_photos (path_stage);
CREATE INDEX ix_path_updated_photos ON path_photos (date_updated);


create table if not exists path_poubelle
(
    id SERIAL primary key,
    path varchar(2000) not null,
    extension varchar(25) default null,
    name varchar(2000) not null,
    owner varchar(255) default null,
    "group" varchar(255) default null,
    root varchar(255) default null,
    drive varchar(25) default null,
    size BIGINT default null,
    hash char(64) default null,
    is_windows_path boolean default null,
    hidden boolean default null,
    archive boolean default null,
    compressed boolean default null,
    encrypted boolean default null,
    offline boolean default null,
    readonly boolean default null,
    system boolean default null,
    temporary boolean default null,
    content_family int default null,
    content_category int default null,
    content_rating int default null,
    content_min_age int default null,
    quality_rating int default null,
    mime_type varchar(255) default null,
    path_type int default null,
    files_in_dir int default null,
    path_stage int default null,
    tags varchar(2000) default null,
    date_created timestamp not null default now(),
    date_updated timestamp not null default now(),
    constraint uk_path_poubelle unique (path),
    constraint fk_path_type_poubelle foreign key (path_type) references path_type(id),
    constraint fk_path_stage_poubelle foreign key (path_stage) references path_stage(id),
    constraint fk_content_family_poubelle foreign key (content_family) references content_family(id),
    constraint fk_content_category_poubelle foreign key (content_category) references content_category(id),
    constraint fk_content_rating_poubelle foreign key (content_rating) references rating(id),
    constraint fk_quality_rating_poubelle foreign key (quality_rating) references rating(id),
    constraint fk_content_min_age_poubelle foreign key (content_min_age) references content_classification_pegi_age(id)
);
CREATE UNIQUE INDEX ix_path_path_poubelle ON path_poubelle (path);
CREATE INDEX ix_path_name_poubelle ON path_poubelle (name);
CREATE INDEX ix_path_ext_poubelle ON path_poubelle(extension);
CREATE INDEX ix_path_drive_poubelle ON path_poubelle (drive);
CREATE INDEX ix_path_size_poubelle ON path_poubelle (size);
CREATE INDEX ix_path_hash_poubelle ON path_poubelle (hash);
CREATE INDEX ix_path_content_poubelle ON path_poubelle (content_family);
CREATE INDEX ix_path_type_poubelle ON path_poubelle (path_type);
CREATE INDEX ix_path_stage_poubelle ON path_poubelle (path_stage);
CREATE INDEX ix_path_updated_poubelle ON path_poubelle (date_updated);


create table if not exists path_projects
(
    id SERIAL primary key,
    path varchar(2000) not null,
    extension varchar(25) default null,
    name varchar(2000) not null,
    owner varchar(255) default null,
    "group" varchar(255) default null,
    root varchar(255) default null,
    drive varchar(25) default null,
    size BIGINT default null,
    hash char(64) default null,
    is_windows_path boolean default null,
    hidden boolean default null,
    archive boolean default null,
    compressed boolean default null,
    encrypted boolean default null,
    offline boolean default null,
    readonly boolean default null,
    system boolean default null,
    temporary boolean default null,
    content_family int default null,
    content_category int default null,
    content_rating int default null,
    content_min_age int default null,
    quality_rating int default null,
    mime_type varchar(255) default null,
    path_type int default null,
    files_in_dir int default null,
    path_stage int default null,
    tags varchar(2000) default null,
    date_created timestamp not null default now(),
    date_updated timestamp not null default now(),
    constraint uk_path_projects unique (path),
    constraint fk_path_type_projects foreign key (path_type) references path_type(id),
    constraint fk_path_stage_projects foreign key (path_stage) references path_stage(id),
    constraint fk_content_family_projects foreign key (content_family) references content_family(id),
    constraint fk_content_category_projects foreign key (content_category) references content_category(id),
    constraint fk_content_rating_projects foreign key (content_rating) references rating(id),
    constraint fk_quality_rating_projects foreign key (quality_rating) references rating(id),
    constraint fk_content_min_age_projects foreign key (content_min_age) references content_classification_pegi_age(id)
);
CREATE UNIQUE INDEX ix_path_path_projects ON path_projects (path);
CREATE INDEX ix_path_name_projects ON path_projects (name);
CREATE INDEX ix_path_ext_projects ON path_projects(extension);
CREATE INDEX ix_path_drive_projects ON path_projects (drive);
CREATE INDEX ix_path_size_projects ON path_projects (size);
CREATE INDEX ix_path_hash_projects ON path_projects (hash);
CREATE INDEX ix_path_content_projects ON path_projects (content_family);
CREATE INDEX ix_path_type_projects ON path_projects (path_type);
CREATE INDEX ix_path_stage_projects ON path_projects (path_stage);
CREATE INDEX ix_path_updated_projects ON path_projects (date_updated);


create table if not exists path_test
(
    id SERIAL primary key,
    path varchar(2000) not null,
    extension varchar(25) default null,
    name varchar(2000) not null,
    owner varchar(255) default null,
    "group" varchar(255) default null,
    root varchar(255) default null,
    drive varchar(25) default null,
    size BIGINT default null,
    hash char(64) default null,
    is_windows_path boolean default null,
    hidden boolean default null,
    archive boolean default null,
    compressed boolean default null,
    encrypted boolean default null,
    offline boolean default null,
    readonly boolean default null,
    system boolean default null,
    temporary boolean default null,
    content_family int default null,
    content_category int default null,
    content_rating int default null,
    content_min_age int default null,
    quality_rating int default null,
    mime_type varchar(255) default null,
    path_type int default null,
    files_in_dir int default null,
    path_stage int default null,
    tags varchar(2000) default null,
    date_created timestamp not null default now(),
    date_updated timestamp not null default now(),
    constraint uk_path_test unique (path),
    constraint fk_path_type_test foreign key (path_type) references path_type(id),
    constraint fk_path_stage_test foreign key (path_stage) references path_stage(id),
    constraint fk_content_family_test foreign key (content_family) references content_family(id),
    constraint fk_content_category_test foreign key (content_category) references content_category(id),
    constraint fk_content_rating_test foreign key (content_rating) references rating(id),
    constraint fk_quality_rating_test foreign key (quality_rating) references rating(id),
    constraint fk_content_min_age_test foreign key (content_min_age) references content_classification_pegi_age(id)
);
CREATE UNIQUE INDEX ix_path_path_test ON path_test (path);
CREATE INDEX ix_path_name_test ON path_test (name);
CREATE INDEX ix_path_ext_test ON path_test(extension);
CREATE INDEX ix_path_drive_test ON path_test (drive);
CREATE INDEX ix_path_size_test ON path_test (size);
CREATE INDEX ix_path_hash_test ON path_test (hash);
CREATE INDEX ix_path_content_test ON path_test (content_family);
CREATE INDEX ix_path_type_test ON path_test (path_type);
CREATE INDEX ix_path_stage_test ON path_test (path_stage);
CREATE INDEX ix_path_updated_test ON path_test (date_updated);



CREATE TABLE IF NOT EXISTS content_tags
(
    path_id                int       NOT NULL,
    tag_id                 int       NOT NULL,
    PRIMARY KEY (path_id, tag_id),
    CONSTRAINT fk_content_tags_tags FOREIGN KEY (tag_id) REFERENCES tags(id),
    CONSTRAINT fk_content_tags_path FOREIGN KEY (path_id) REFERENCES path(id)
);

CREATE TABLE IF NOT EXISTS content_files
(
    content_id              int       NOT NULL,
    path_id                 int       NOT NULL,
    PRIMARY KEY (content_id, path_id),
    CONSTRAINT fk_content_files_content FOREIGN KEY (content_id) REFERENCES content(id),
    CONSTRAINT fk_content_files_path FOREIGN KEY (path_id) REFERENCES path(id)
);
CREATE INDEX ix_content_files_id ON content_files (content_id, path_id);
