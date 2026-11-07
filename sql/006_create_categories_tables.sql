-- AradLens - categorii pentru locatii
-- Motor: MySQL / MariaDB (>= 5.7 / 10.3), charset utf8mb4, engine InnoDB
-- O locatie are o singura categorie (locations.category_id).

CREATE TABLE IF NOT EXISTS categories (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name        VARCHAR(100)    NOT NULL,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_categories_name (name)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
