import "@testing-library/jest-dom";
import { vi } from "vitest";
import { initialData } from "@/lib/kanban";

const jsonResponse = (data: unknown) =>
	new Response(JSON.stringify(data), {
		status: 200,
		headers: { "Content-Type": "application/json" },
	});

vi.stubGlobal(
	"fetch",
	vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
		const url = typeof input === "string" ? input : input.toString();
		const method = init?.method ?? "GET";

		if (url.includes("/api/ai/structured")) {
			return jsonResponse({
				message: "AI response",
				updated: false,
				board: initialData,
			});
		}

		if (method === "PUT") {
			const body = init?.body ? JSON.parse(init.body as string) : initialData;
			return jsonResponse(body);
		}
		return jsonResponse(initialData);
	})
);
