/*
Copyright 2015 Ericsson AB

Licensed under the Apache License, Version 2.0 (the 'License'); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
*/

DROP DATABASE IF EXISTS clients;
CREATE DATABASE clients;
USE clients;

CREATE TABLE client_profile (
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(255),
    pass CHAR(40),
    email VARCHAR(255),
    phone VARCHAR(15),
    language VARCHAR(2) DEFAULT 'en',
    store_location VARCHAR(1) DEFAULT '1',
    notifications_alert VARCHAR(1) DEFAULT '1',
    recommendations_alert VARCHAR(1) DEFAULT '1',
    theme VARCHAR(1) DEFAULT '1',
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    google_registration_token VARCHAR(255),
    PRIMARY KEY (id)
);

DELIMITER $$
CREATE FUNCTION client_sign_up (
    in_username VARCHAR(255),
    in_pass CHAR(40),
    in_email VARCHAR(255),
    in_phone VARCHAR(15),
    in_google_registration_token VARCHAR(255)
)
RETURNS TEXT
BEGIN
    DECLARE code CHAR(5) DEFAULT '00000';
    DECLARE rows INT;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            code = RETURNED_SQLSTATE;
    END;

	IF EXISTS (
		SELECT username
		FROM client_profile
		WHERE username = in_username
	)
	THEN
		RETURN '01';
	ELSEIF EXISTS (
		SELECT email
		FROM client_profile
		WHERE email = in_email
	)
	THEN
		RETURN '02';
	ELSEIF EXISTS (
		SELECT phone
		FROM client_profile
		WHERE phone = in_phone
	)
	THEN
		RETURN '03';
	ELSE
        INSERT INTO client_profile (username, pass, email, phone, google_registration_token)
        VALUES (in_username, in_pass, in_email, in_phone, in_google_registration_token);

        GET DIAGNOSTICS rows = ROW_COUNT;

        IF code = '00000' AND rows = 1 THEN
            RETURN CONCAT('1', '|', (SELECT LAST_INSERT_ID()));
        ELSE
            RETURN '0';
        END IF;
    END IF;
END $$

CREATE FUNCTION client_sign_in (
    in_username VARCHAR(255),
    in_pass CHAR(40),
    in_google_registration_token VARCHAR(255)
)
RETURNS TEXT
BEGIN
    DECLARE ret_id INT;
    DECLARE ret_email VARCHAR(255);
    DECLARE ret_phone VARCHAR(15);
    DECLARE ret_language VARCHAR(2);
    DECLARE ret_store_location VARCHAR(1);
    DECLARE ret_notifications_alert VARCHAR(1);
    DECLARE ret_recommendations_alert VARCHAR(1);
    DECLARE ret_theme VARCHAR(1);

    DECLARE code CHAR(5) DEFAULT '00000';
    DECLARE rows INT;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            code = RETURNED_SQLSTATE;
    END;

    SELECT
        id, email, phone, language, store_location,
        notifications_alert, recommendations_alert, theme
    INTO
        ret_id, ret_email, ret_phone, ret_language, ret_store_location,
        ret_notifications_alert, ret_recommendations_alert, ret_theme
    FROM client_profile
    WHERE username = in_username AND pass = in_pass;

    GET DIAGNOSTICS rows = ROW_COUNT;

    IF code = '00000' AND rows = 1 THEN
        UPDATE client_profile
        SET google_registration_token = in_google_registration_token
        WHERE id = ret_id;

        RETURN CONCAT(
            '1', '|', ret_id, '|', ret_email, '|', ret_phone, '|', ret_language, '|',
            ret_store_location, '|', ret_notifications_alert, '|',
            ret_recommendations_alert, '|', ret_theme
        );
    ELSE
        RETURN '0';
    END IF;
END $$

CREATE FUNCTION google_sign_in (
    in_email VARCHAR(255)
)
RETURNS TEXT
BEGIN
    DECLARE ret_id INT;
    DECLARE ret_username VARCHAR(255);
    DECLARE temp_pass CHAR(40);
    DECLARE ret_pass VARCHAR(1);
    DECLARE ret_phone VARCHAR(15);
    DECLARE ret_language VARCHAR(2);
    DECLARE ret_store_location VARCHAR(1);
    DECLARE ret_notifications_alert VARCHAR(1);
    DECLARE ret_recommendations_alert VARCHAR(1);
    DECLARE ret_theme VARCHAR(1);

    DECLARE code CHAR(5) DEFAULT '00000';
    DECLARE rows INT;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
        code = RETURNED_SQLSTATE;
    END;

    IF EXISTS (
        SELECT email
        FROM client_profile
        WHERE email = in_email
    )
    THEN
        SELECT
            id, username, pass, phone, language, store_location,
            notifications_alert, recommendations_alert, theme
        INTO
            ret_id, ret_username, temp_pass, ret_phone, ret_language, ret_store_location,
            ret_notifications_alert, ret_recommendations_alert, ret_theme
        FROM client_profile
        WHERE email = in_email;

        IF temp_pass = '' THEN
            SET ret_pass = '0';
        ELSE
            SET ret_pass = '1';
        END IF;

        GET DIAGNOSTICS rows = ROW_COUNT;

        IF code = '00000' AND rows = 1 THEN
            RETURN CONCAT(
                '1', '|', ret_id, '|', ret_username, '|', ret_pass, '|', ret_phone, '|', ret_language, '|',
                ret_store_location, '|', ret_notifications_alert, '|',
                ret_recommendations_alert, '|', ret_theme
            );
        ELSE
            RETURN '0';
        END IF;
    ELSE
        RETURN google_sign_up(in_email);
    END IF;
END $$

CREATE FUNCTION google_sign_up (
    in_email VARCHAR(255)
)
RETURNS TEXT
BEGIN
    DECLARE code CHAR(5) DEFAULT '00000';
    DECLARE rows INT;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            code = RETURNED_SQLSTATE;
    END;

    INSERT INTO client_profile (username, pass, email, phone)
    VALUES ('', '', in_email, '');

    GET DIAGNOSTICS rows = ROW_COUNT;

    IF code = '00000' AND rows = 1 THEN
        RETURN CONCAT('2', '|', (SELECT LAST_INSERT_ID()));
    ELSE
        RETURN '0';
    END IF;
END $$

CREATE FUNCTION client_profile_update (
    in_id INT,
    in_username VARCHAR(255),
    in_email VARCHAR(255),
    in_phone VARCHAR(15)
)
RETURNS TEXT
BEGIN
    DECLARE code CHAR(5) DEFAULT '00000';
    DECLARE rows INT;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            code = RETURNED_SQLSTATE;
    END;

    IF EXISTS (
        SELECT username
        FROM client_profile
        WHERE username = in_username AND id <> in_id
    )
    THEN
        RETURN '01';
    ELSEIF EXISTS (
        SELECT email
        FROM client_profile
        WHERE email = in_email AND id <> in_id
    )
    THEN
        RETURN '02';
    ELSEIF EXISTS (
        SELECT phone
        FROM client_profile
        WHERE phone = in_phone AND id <> in_id
    )
    THEN
        RETURN '03';
    ELSE
        UPDATE client_profile
        SET username = in_username,
            email = in_email,
            phone = in_phone
        WHERE id = in_id;
        GET DIAGNOSTICS rows = ROW_COUNT;

        IF code = '00000' AND rows > 0 THEN
            RETURN '1';
        ELSE
            RETURN '0';
        END IF;
    END IF;
END $$

CREATE FUNCTION client_settings_update (
    in_id INT,
    in_language VARCHAR(2),
    in_store_location VARCHAR(1),
    in_notifications_alert VARCHAR(1),
    in_recommendations_alert VARCHAR(1),
    in_theme VARCHAR(1)
)
RETURNS TEXT
BEGIN
    DECLARE code CHAR(5) DEFAULT '00000';
    DECLARE rows INT;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            code = RETURNED_SQLSTATE;
    END;

    UPDATE client_profile
    SET language = in_language,
        store_location = in_store_location,
        notifications_alert = in_notifications_alert,
        recommendations_alert = in_recommendations_alert,
        theme = in_theme
    WHERE id = in_id;

    GET DIAGNOSTICS rows = ROW_COUNT;

    IF code = '00000' AND rows > 0 THEN
        RETURN '1';
    ELSE
        RETURN '0';
    END IF;
END $$

CREATE FUNCTION client_existing_password_update (
    in_id INT,
    in_old_pass CHAR(40),
    in_new_pass CHAR(40)
)
RETURNS TEXT
BEGIN
    DECLARE code CHAR(5) DEFAULT '00000';
    DECLARE rows INT;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            code = RETURNED_SQLSTATE;
    END;

    UPDATE client_profile
    SET pass = in_new_pass
    WHERE id = in_id AND pass = in_old_pass;

    GET DIAGNOSTICS rows = ROW_COUNT;

    IF code = '00000' AND rows > 0 THEN
        RETURN '1';
    ELSE
        RETURN '0';
    END IF;
END $$

CREATE FUNCTION client_forgotten_password_reset (
    in_email VARCHAR(255),
    in_new_pass CHAR(40)
)
RETURNS TEXT
BEGIN
    DECLARE code CHAR(5) DEFAULT '00000';
    DECLARE rows INT;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            code = RETURNED_SQLSTATE;
    END;

    UPDATE client_profile
    SET pass = in_new_pass
    WHERE email = in_email;

    GET DIAGNOSTICS rows = ROW_COUNT;

    IF code = '00000' AND rows > 0 THEN
        RETURN '1';
    ELSE
        RETURN '0';
    END IF;
END $$

CREATE FUNCTION get_google_registration_token (
    in_id INT
)
RETURNS VARCHAR(255)
BEGIN
    DECLARE ret_google_registration_token VARCHAR(255);
    DECLARE code CHAR(5) DEFAULT '00000';
    DECLARE rows INT;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            code = RETURNED_SQLSTATE;
    END;

    SELECT google_registration_token
    INTO ret_google_registration_token
    FROM client_profile
    WHERE id = in_id;

    GET DIAGNOSTICS rows = ROW_COUNT;

    IF code = '00000' AND rows > 0 THEN
        RETURN ret_google_registration_token;
    ELSE
        RETURN '';
    END IF;
END $$

DELIMITER ;
