CREATE DATABASE IF NOT EXISTS `chaplin_tcc`;
USE `chaplin_tcc`;

-- 1. TABELA DE USUÁRIOS (AUTH_USER)
CREATE TABLE `auth_user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `password` VARCHAR(128) NOT NULL,
  `last_login` DATETIME NULL,
  `is_superuser` TINYINT(1) NOT NULL,
  `username` VARCHAR(150) NOT NULL UNIQUE,
  `first_name` VARCHAR(150) NOT NULL,
  `last_name` VARCHAR(150) NOT NULL,
  `email` VARCHAR(254) NOT NULL,
  `is_staff` TINYINT(1) NOT NULL,
  `is_active` TINYINT(1) NOT NULL,
  `date_joined` DATETIME NOT NULL,
  PRIMARY KEY (`id`)
);

-- 2. TABELA DE ESPECIALIDADES DO COLABORADOR
CREATE TABLE `users_especialidade` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL UNIQUE,
  `descricao` LONGTEXT NOT NULL,
  `created_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`)
);

-- 3. TABELA DE PERFIL DE USUÁRIO (EXTENSÃO DA AUTH_USER)
CREATE TABLE `users_userprofile` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL UNIQUE,
  `role` VARCHAR(20) NOT NULL,
  `especialidade_id` INT NULL,
  `phone` VARCHAR(20) NOT NULL,
  `avatar` VARCHAR(100) NULL,
  `company_name` VARCHAR(200) NOT NULL,
  `cpf` VARCHAR(14) NOT NULL,
  `cnpj` VARCHAR(18) NOT NULL,
  `bio` LONGTEXT NOT NULL,
  `cep` VARCHAR(9) NOT NULL,
  `logradouro` VARCHAR(255) NOT NULL,
  `numero` VARCHAR(20) NOT NULL,
  `complemento` VARCHAR(100) NOT NULL,
  `bairro` VARCHAR(100) NOT NULL,
  `cidade` VARCHAR(100) NOT NULL,
  `estado` VARCHAR(2) NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_userprofile_user` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `fk_userprofile_especialidade` FOREIGN KEY (`especialidade_id`) REFERENCES `users_especialidade` (`id`)
);

-- 4. TABELA DE LOG DE ATIVIDADES (AUDITORIA)
CREATE TABLE `users_activitylog` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `admin_user_id` INT NULL,
  `target_user_id` INT NULL,
  `action` VARCHAR(255) NOT NULL,
  `role_old` VARCHAR(50) NULL,
  `role_new` VARCHAR(50) NULL,
  `timestamp` DATETIME NOT NULL,
  `ip_address` CHAR(39) NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_activitylog_admin` FOREIGN KEY (`admin_user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `fk_activitylog_target` FOREIGN KEY (`target_user_id`) REFERENCES `auth_user` (`id`)
);

-- 5. TABELA DE TAREFAS / TICKETS
CREATE TABLE `tasks_task` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(200) NOT NULL,
  `description` LONGTEXT NOT NULL,
  `priority` VARCHAR(20) NOT NULL,
  `status` VARCHAR(20) NOT NULL,
  `created_by_id` INT NULL,
  `assigned_to_id` INT NULL,
  `assigned_leader_id` INT NULL,
  `due_date` DATE NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  `completed_at` DATETIME NULL,
  `location` VARCHAR(200) NOT NULL,
  `cep` VARCHAR(9) NOT NULL,
  `logradouro` VARCHAR(200) NOT NULL,
  `numero` VARCHAR(20) NOT NULL,
  `complemento` VARCHAR(100) NOT NULL,
  `bairro` VARCHAR(100) NOT NULL,
  `cidade` VARCHAR(100) NOT NULL,
  `estado` VARCHAR(2) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_task_created_by` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `fk_task_assigned_to` FOREIGN KEY (`assigned_to_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `fk_task_assigned_leader` FOREIGN KEY (`assigned_leader_id`) REFERENCES `auth_user` (`id`)
);

-- 6. TABELA DE EVIDÊNCIAS DE TAREFA (FOTOS)
CREATE TABLE `tasks_taskevidence` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `task_id` INT NOT NULL,
  `photo` VARCHAR(100) NOT NULL,
  `description` LONGTEXT NOT NULL,
  `created_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_taskevidence_task` FOREIGN KEY (`task_id`) REFERENCES `tasks_task` (`id`)
);

-- 7. TABELA DE MENSAGENS (CHAT) DA TAREFA
CREATE TABLE `tasks_message` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `task_id` INT NOT NULL,
  `sender_id` INT NULL,
  `content` LONGTEXT NOT NULL,
  `created_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_message_task` FOREIGN KEY (`task_id`) REFERENCES `tasks_task` (`id`),
  CONSTRAINT `fk_message_sender` FOREIGN KEY (`sender_id`) REFERENCES `auth_user` (`id`)
);

-- 8. TABELA DE NOTIFICAÇÕES (SISTEMA DE AVISOS)
CREATE TABLE `tasks_notification` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `recipient_id` INT NOT NULL,
  `task_id` INT NULL,
  `tipo` VARCHAR(30) NOT NULL,
  `titulo` VARCHAR(200) NOT NULL,
  `mensagem` LONGTEXT NOT NULL,
  `lida` TINYINT(1) NOT NULL,
  `created_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_notification_recipient` FOREIGN KEY (`recipient_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `fk_notification_task` FOREIGN KEY (`task_id`) REFERENCES `tasks_task` (`id`)
);
