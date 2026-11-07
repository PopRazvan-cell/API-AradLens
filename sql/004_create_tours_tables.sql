-- AradLens - tururi ghidate: lant ordonat de locatii
-- Motor: MySQL / MariaDB (>= 5.7 / 10.3), charset utf8mb4, engine InnoDB

CREATE TABLE IF NOT EXISTS tours (
    id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name         VARCHAR(150)    NOT NULL,
    description  TEXT            NULL,
    created_at   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_tours_name (name)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tour_locations (
    id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    tour_id      BIGINT UNSIGNED NOT NULL,
    location_id  BIGINT UNSIGNED NOT NULL,
    `position`   INT             NOT NULL,
    PRIMARY KEY (id),
    KEY idx_tour_locations_tour_id (tour_id),
    KEY idx_tour_locations_location_id (location_id),
    CONSTRAINT fk_tour_locations_tour
        FOREIGN KEY (tour_id) REFERENCES tours (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_tour_locations_location
        FOREIGN KEY (location_id) REFERENCES locations (id)
        ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
