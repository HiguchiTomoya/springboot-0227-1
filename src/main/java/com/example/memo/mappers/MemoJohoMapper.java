package com.example.memo.mappers;

import java.util.Date;
import java.util.List;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import com.example.memo.entities.MemoJoho;

@Mapper
public interface MemoJohoMapper {

	//メモ情報を追加する
	void insertMemoJoho(@Param("body") String body, @Param("createdDate") Date createdDate);

	//すべてのメモ情報を取得する
	List<MemoJoho> getAllMemoJoho();

	//１件のみメモ情報を取得する
	MemoJoho getMemoJoho(@Param("id") int id);

	//メモ情報を編集する
	void editMemoJoho(@Param("id") int id, @Param("body") String body);

	//メモ情報を削除する
	void deleteMemoJoho(@Param("id") int id);
}
