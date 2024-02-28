package com.example.memo.entities;

import java.sql.Date;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Entity
public class MemoJoho {
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private int id;

	// 本文
	@Column(name = "body", nullable = false)
	private String body;

	// 作成日時
	@Column(name = "createddate", nullable = false)
	private Date createddate;
}
