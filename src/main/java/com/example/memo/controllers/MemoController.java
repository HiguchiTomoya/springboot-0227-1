package com.example.memo.controllers;

import java.util.Date;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

import com.example.memo.entities.MemoJoho;
import com.example.memo.mappers.MemoJohoMapper;

@Controller
public class MemoController {
	@Autowired
	MemoJohoMapper memoJohoMapper;

	public MemoController(MemoJohoMapper memoJohoMapper) {
		this.memoJohoMapper = memoJohoMapper;
	}

	//初期画面
	@GetMapping("/")
	public String index() {
		return "redirect:/memoIchiran";
	}

	//メモ一覧画面
	@GetMapping("/memoIchiran")
	public String memoIchiran(Model model) {
		// SELECT文の呼び出し
		List<MemoJoho> memoJohoList = memoJohoMapper.getAllMemoJoho();

		model.addAttribute("memoJohoList", memoJohoList);
		model.addAttribute("main", "layouts/memoIchiran::memoIchiran_fragment");
		return "default";
	}

	//メモ追加画面
	@GetMapping("/memoInsert")
	public String memoInsert(Model model) {
		model.addAttribute("main", "layouts/memoInsert::memoInsert_fragment");
		return "default";

	}

	@PostMapping("/memoInsertSubmit")
	public String memoInsertSubmit(
			@RequestParam(defaultValue = "") String body,
			Model model) {

		// java.util.Dateからjava.sql.Dateへの変換
		var date = new Date();
		java.sql.Date sqlDate = new java.sql.Date(date.getTime());

		// INSERT文の呼び出し
		memoJohoMapper.insertMemoJoho(body, sqlDate);

		// 日記一覧へリダイレクト
		return "redirect:/memoIchiran";
	}

	//メモ編集画面
	@GetMapping("/memoEdit/{id}")
	public String memoEdit(@PathVariable("id") int id,
			Model model) {
		model.addAttribute("memoJoho", memoJohoMapper.getMemoJoho(id));
		model.addAttribute("main", "layouts/memoEdit::memoEdit_fragment");
		return "default";

	}

	@PostMapping("/memoUpdateSubmit/{id}")
	public String memoUpdateSubmit(
			@PathVariable("id") int id,
			@RequestParam(defaultValue = "") String body,
			Model model) {

		// UPDATE文の呼び出し
		memoJohoMapper.editMemoJoho(id, body);

		// 日記一覧へリダイレクト
		return "redirect:/memoIchiran";
	}

	//メモ削除画面
	@GetMapping("/memoDelete/{id}")
	public String memoDelete(@PathVariable("id") int id,
			Model model) {
		memoJohoMapper.deleteMemoJoho(id); // 日記一覧へリダイレクト
		return "redirect:/memoIchiran";
	}
}
