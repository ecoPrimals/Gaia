using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using Godot;
using Godot.Collections;

public partial class Asana : Node
{
	public delegate bool ProgressUpdateDelegate(float progressZeroToOne, string failedWithErrorMessage);

	private struct Response
	{
		public ResponseData data { get; set; }
	}

	private struct ResponseData
	{
		public string gid { get; set; }
	}

	public struct Attachment
	{
		public string filename;

		public AttachmentType attachmentType;

		public byte[] bytes;
	}

	public enum AttachmentType
	{
		Jpg,
		Png,
		Zip,
		Json,
		Txt,
		OtherBinary
	}

	private struct FileAttachment
	{
		public string fieldName;

		public string filename;

		public byte[] bytes;

		public string mimeType;
	}

	private struct MultipartData
	{
		public byte[] body;

		public string boundary;
	}

	private const string asanaAuth = "1/1205359767726227:42f1c1ad81e5aeba26e4dded8935e134";

	private const string projectId = "1211506956200687";

	public int TimeoutSeconds = 20;

	public async void Upload(string asanaTitle, string description, List<Attachment> attachments, string assignToAsanaUserEmail, ProgressUpdateDelegate progressDelegate = null)
	{
		await UploadAsync(asanaTitle, description, attachments, assignToAsanaUserEmail, progressDelegate);
	}

	public async Task UploadAsync(string asanaTitle, string description, List<Attachment> attachments, string assignToAsanaUserEmail, ProgressUpdateDelegate progressDelegate = null)
	{
		GD.Print("Sending Asana task: " + asanaTitle);
		int totalTaskCount = 1 + attachments.Count;
		string taskID;
		try
		{
			Dictionary dictionary = new Dictionary();
			dictionary["name"] = asanaTitle;
			dictionary["notes"] = description;
			if (!string.IsNullOrEmpty(assignToAsanaUserEmail))
			{
				dictionary["assignee"] = assignToAsanaUserEmail;
			}
			Godot.Collections.Array array = new Godot.Collections.Array();
			array.Add("1211506956200687");
			dictionary["projects"] = array;
			Dictionary jsonData = new Dictionary { { "data", dictionary } };
			string text = await MakeJsonRequestAsync("https://app.asana.com/api/1.0/tasks", jsonData, progressDelegate, 0, totalTaskCount);
			if (text == null)
			{
				return;
			}
			Variant variant = Json.ParseString(text);
			if (!variant.AsGodotDictionary().ContainsKey("data"))
			{
				string text2 = "Failed to parse Asana response";
				GD.PrintErr(text2);
				progressDelegate?.Invoke(0f, text2);
				return;
			}
			Dictionary dictionary2 = variant.AsGodotDictionary()["data"].AsGodotDictionary();
			taskID = dictionary2["gid"].AsString();
		}
		catch (Exception ex)
		{
			string text3 = "Sorry, feedback couldn't be sent because an error occurred: " + ex.Message;
			GD.PrintErr(text3);
			progressDelegate?.Invoke(0f, text3);
			return;
		}
		int attachmentIdx = 0;
		foreach (Attachment attachment in attachments)
		{
			try
			{
				string mimeType = GetMimeType(attachment.attachmentType);
				System.Collections.Generic.Dictionary<string, object> fields = new System.Collections.Generic.Dictionary<string, object>
				{
					{ "resource_subtype", "asana" },
					{ "parent", taskID }
				};
				FileAttachment value = new FileAttachment
				{
					fieldName = "file",
					filename = attachment.filename,
					bytes = attachment.bytes,
					mimeType = mimeType
				};
				MultipartData bodyData = BuildMultipartFormData(fields, value);
				if (await MakeHttpRequestAsync("https://app.asana.com/api/1.0/attachments", bodyData, progressDelegate, 1 + attachmentIdx, totalTaskCount) == null)
				{
					return;
				}
			}
			catch (Exception ex2)
			{
				string text4 = "Sorry, feedback couldn't be sent because an error occurred: " + ex2.Message;
				GD.PrintErr(text4);
				progressDelegate?.Invoke(0f, text4);
				return;
			}
			attachmentIdx++;
		}
		progressDelegate?.Invoke(1f, null);
	}

	private string GetMimeType(AttachmentType attachmentType)
	{
		return attachmentType switch
		{
			AttachmentType.Jpg => "image/jpeg", 
			AttachmentType.Png => "image/png", 
			AttachmentType.Zip => "application/zip", 
			AttachmentType.Json => "application/json", 
			AttachmentType.Txt => "text/plain", 
			AttachmentType.OtherBinary => "application/octet-stream", 
			_ => throw new Exception("Unhandled attachment type: " + attachmentType), 
		};
	}

	private MultipartData BuildMultipartFormData(System.Collections.Generic.Dictionary<string, object> fields, FileAttachment? file)
	{
		string boundary = "----GodotFormBoundary" + Guid.NewGuid().ToString("N");
		List<byte> bodyBytes = new List<byte>();
		foreach (KeyValuePair<string, object> field in fields)
		{
			if (field.Value is string value)
			{
				AddTextPart(field.Key, value);
			}
			else if (field.Value is IEnumerable<string> enumerable)
			{
				string name = (field.Key.EndsWith("[]") ? field.Key : (field.Key + "[]"));
				foreach (string item in enumerable)
				{
					AddTextPart(name, item);
				}
			}
			else if (field.Value != null)
			{
				AddTextPart(field.Key, field.Value.ToString());
			}
		}
		if (file.HasValue)
		{
			FileAttachment value2 = file.Value;
			string s = $"--{boundary}\r\nContent-Disposition: form-data; name=\"{value2.fieldName}\"; filename=\"{value2.filename}\"\r\nContent-Type: {value2.mimeType}\r\n\r\n";
			bodyBytes.AddRange(Encoding.UTF8.GetBytes(s));
			bodyBytes.AddRange(value2.bytes);
			bodyBytes.AddRange(Encoding.UTF8.GetBytes("\r\n"));
		}
		bodyBytes.AddRange(Encoding.UTF8.GetBytes("--" + boundary + "--\r\n"));
		return new MultipartData
		{
			body = bodyBytes.ToArray(),
			boundary = boundary
		};
		void AddTextPart(string value3, string value4)
		{
			string s2 = $"--{boundary}\r\nContent-Disposition: form-data; name=\"{value3}\"\r\n\r\n{value4}\r\n";
			bodyBytes.AddRange(Encoding.UTF8.GetBytes(s2));
		}
	}

	private async Task<string> MakeHttpRequestAsync(string url, MultipartData bodyData, ProgressUpdateDelegate progressDelegate, int currentTaskIndex, int totalTaskCount)
	{
		HttpRequest httpRequest = new HttpRequest();
		AddChild(httpRequest, forceReadableName: false, InternalMode.Disabled);
		string[] customHeaders = new string[2]
		{
			"Authorization: Bearer 1/1205359767726227:42f1c1ad81e5aeba26e4dded8935e134",
			"Content-Type: multipart/form-data; boundary=" + bodyData.boundary
		};
		httpRequest.Timeout = TimeoutSeconds;
		Error error = httpRequest.RequestRaw(url, customHeaders, HttpClient.Method.Post, bodyData.body);
		if (error != Error.Ok)
		{
			string text = "HTTP Request failed with error: " + error;
			GD.PrintErr(text);
			progressDelegate?.Invoke(0f, text);
			httpRequest.QueueFree();
			return null;
		}
		bool completed = false;
		long httpResult = 0L;
		long responseCode = 0L;
		byte[] resultBody = null;
		httpRequest.RequestCompleted += delegate(long result, long code, string[] _headers, byte[] body)
		{
			completed = true;
			httpResult = result;
			responseCode = code;
			resultBody = body;
		};
		while (!completed)
		{
			await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
			if (progressDelegate != null)
			{
				float num = 0.5f;
				float progressZeroToOne = ((float)currentTaskIndex + num) / (float)totalTaskCount;
				if (progressDelegate(progressZeroToOne, null))
				{
					httpRequest.CancelRequest();
					httpRequest.QueueFree();
					return null;
				}
			}
		}
		if (httpResult != 0L || responseCode < 200 || responseCode >= 300)
		{
			string value = ((resultBody != null) ? resultBody.GetStringFromUtf8() : "");
			string text2 = $"Sorry, feedback couldn't be sent because an error occurred: {(HttpRequest.Result)httpResult} (HTTP {responseCode})\n{value}";
			GD.PrintErr(text2);
			progressDelegate?.Invoke(0f, text2);
			httpRequest.QueueFree();
			return null;
		}
		string stringFromUtf = resultBody.GetStringFromUtf8();
		httpRequest.QueueFree();
		return stringFromUtf;
	}

	private async Task<string> MakeJsonRequestAsync(string url, Dictionary jsonData, ProgressUpdateDelegate progressDelegate, int currentTaskIndex, int totalTaskCount)
	{
		HttpRequest httpRequest = new HttpRequest();
		AddChild(httpRequest, forceReadableName: false, InternalMode.Disabled);
		string s = Json.Stringify(jsonData);
		byte[] bytes = Encoding.UTF8.GetBytes(s);
		string[] customHeaders = new string[3] { "Authorization: Bearer 1/1205359767726227:42f1c1ad81e5aeba26e4dded8935e134", "Content-Type: application/json", "Accept: application/json" };
		httpRequest.Timeout = TimeoutSeconds;
		Error error = httpRequest.RequestRaw(url, customHeaders, HttpClient.Method.Post, bytes);
		if (error != Error.Ok)
		{
			string text = "HTTP Request failed with error: " + error;
			GD.PrintErr(text);
			progressDelegate?.Invoke(0f, text);
			httpRequest.QueueFree();
			return null;
		}
		bool completed = false;
		long httpResult = 0L;
		long responseCode = 0L;
		byte[] resultBody = null;
		httpRequest.RequestCompleted += delegate(long result, long code, string[] _headers, byte[] body)
		{
			completed = true;
			httpResult = result;
			responseCode = code;
			resultBody = body;
		};
		while (!completed)
		{
			await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
			if (progressDelegate != null)
			{
				float num = 0.5f;
				float progressZeroToOne = ((float)currentTaskIndex + num) / (float)totalTaskCount;
				if (progressDelegate(progressZeroToOne, null))
				{
					httpRequest.CancelRequest();
					httpRequest.QueueFree();
					return null;
				}
			}
		}
		if (httpResult != 0L || responseCode < 200 || responseCode >= 300)
		{
			string value = ((resultBody != null) ? resultBody.GetStringFromUtf8() : "");
			string text2 = $"Sorry, feedback couldn't be sent because an error occurred: {(HttpRequest.Result)httpResult} (HTTP {responseCode})\n{value}";
			GD.PrintErr(text2);
			progressDelegate?.Invoke(0f, text2);
			httpRequest.QueueFree();
			return null;
		}
		string stringFromUtf = resultBody.GetStringFromUtf8();
		httpRequest.QueueFree();
		return stringFromUtf;
	}
}
