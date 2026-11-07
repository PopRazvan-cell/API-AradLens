-- AradLens - tabela pentru autentificarea administratorilor
-- Motor: MySQL / MariaDB (>= 5.7 / 10.3), charset utf8mb4, engine InnoDB

CREATE DATABASE IF NOT EXISTS AradLens
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE AradLens;

CREATE TABLE IF NOT EXISTS admins (
    id             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    username       VARCHAR(50)     NOT NULL,
    email          VARCHAR(255)    NOT NULL,
    password_hash  VARCHAR(255)    NOT NULL,
    role           ENUM('superadmin', 'admin') NOT NULL DEFAULT 'admin',
    is_active      TINYINT(1)      NOT NULL DEFAULT 1,
    last_login_at  DATETIME        NULL DEFAULT NULL,
    created_at     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_admins_username (username),
    UNIQUE KEY uq_admins_email (email),
    KEY idx_admins_is_active (is_active)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- Contul de admin initial este creat automat de aplicatie la pornire
-- (app/init_db.py), folosind variabilele de mediu ADMIN_USERNAME,
-- ADMIN_EMAIL si ADMIN_PASSWORD. Astfel parola este hash-uita corect (bcrypt).
