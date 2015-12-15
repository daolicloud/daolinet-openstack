DROP TABLE IF EXISTS `subnets`;
CREATE TABLE `subnets` (
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `id` varchar(36) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `cidr` varchar(64) NOT NULL,
  `gateway_ip` varchar(64) DEFAULT NULL,
  `network_id` varchar(36) NOT NULL,
  `user_id` varchar(36) NOT NULL,
  `deleted` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `ipallocationpools`;
CREATE TABLE `ipallocationpools` (
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `id` varchar(36) NOT NULL,
  `subnet_id` varchar(36) DEFAULT NULL,
  `first_ip` varchar(64) NOT NULL,
  `last_ip` varchar(64) NOT NULL,
  `deleted` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `subnet_id` (`subnet_id`),
  CONSTRAINT `ipallocationpools_ibfk_1` FOREIGN KEY (`subnet_id`) REFERENCES `subnets` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `ipavailabilityranges`;
CREATE TABLE `ipavailabilityranges` (
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `allocation_pool_id` varchar(36) NOT NULL,
  `first_ip` varchar(64) NOT NULL,
  `last_ip` varchar(64) NOT NULL,
  `deleted` int(11) DEFAULT NULL,
  PRIMARY KEY (`allocation_pool_id`),
  CONSTRAINT `ipavailabilityranges_ibfk_1` FOREIGN KEY (`allocation_pool_id`) REFERENCES `ipallocationpools` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `groups`;
CREATE TABLE `groups` (
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` varchar(255),
  `project_id` varchar(36) NOT NULL,
  `deleted` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `group_members`;
CREATE TABLE `group_members` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `instance_id` varchar(36) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `group_mbmers_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`),
  UNIQUE KEY `uniq_group_member0group_id0instance_id` (`group_id`,`instance_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `firewalls`;
CREATE TABLE `firewalls` (
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `id` varchar(36) NOT NULL,
  `hostname` varchar(255) NOT NULL,
  `gateway_port` int(11) NOT NULL,
  `service_port` int(11) NOT NULL,
  `instance_id` varchar(36) NOT NULL,
  `fake_zone` tinyint(1) NOT NULL,
  `deleted` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `gateways`;
CREATE TABLE `gateways` (
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `datapath_id` varchar(255) NOT NULL,
  `hostname` varchar(255) NOT NULL,
  `idc_id` int(11) NOT NULL,
  `idc_mac` varchar(64) DEFAULT NULL,
  `vint_dev` varchar(255) NOT NULL,
  `vint_mac` varchar(64) NOT NULL,
  `vext_dev` varchar(255) NOT NULL,
  `vext_ip` varchar(64),
  `ext_dev` varchar(255) NOT NULL,
  `ext_mac` varchar(64) NOT NULL,
  `ext_ip` varchar(64) NOT NULL,
  `int_dev` varchar(255) NOT NULL,
  `int_mac` varchar(64) NOT NULL,
  `int_ip` varchar(64) DEFAULT NULL,
  `zone_id` varchar(36) NOT NULL,
  `count` int(11) NOT NULL,
  `is_gateway` tinyint(1) DEFAULT 0,
  `disabled` tinyint(1) DEFAULT 0,
  `deleted` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `singroups`;
CREATE TABLE `singroups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `start` varchar(36) NOT NULL,
  `end` varchar(36) NOT NULL,
  `project_id` varchar(36) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_singroup0start0end0project_id` (`start`,`end`,`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
