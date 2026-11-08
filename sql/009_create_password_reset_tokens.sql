-- AradLens - tokenuri pentru resetarea parolei adminilor
-- Motor: MySQL / MariaDB (>= 5.7 / 10.3), charset utf8mb4, engine InnoDB

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    admin_id    BIGINT UNSIGNED NOT NULL,
    token_hash  CHAR(64)        NOT NULL,
    expires_at  DATETIME        NOT NULL,
    used_at     DATETIME        NULL DEFAULT NULL,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_password_reset_tokens_token_hash (token_hash),
    KEY idx_password_reset_tokens_admin_id (admin_id),
    CONSTRAINT fk_password_reset_tokens_admin
        FOREIGN KEY (admin_id) REFERENCES admins (id)
        ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
