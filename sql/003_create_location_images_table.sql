-- AradLens - galerie de poze pentru locații (relatie one-to-many)
-- Motor: MySQL / MariaDB (>= 5.7 / 10.3), charset utf8mb4, engine InnoDB

CREATE TABLE IF NOT EXISTS location_images (
    id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    location_id  BIGINT UNSIGNED NOT NULL,
    image        VARCHAR(500)    NOT NULL,
    created_at   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_location_images_location_id (location_id),
    CONSTRAINT fk_location_images_location
        FOREIGN KEY (location_id) REFERENCES locations (id)
        ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
