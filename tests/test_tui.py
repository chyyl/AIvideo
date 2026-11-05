import asyncio

from aivscript.app import AIVScriptApp


def test_tui_generates_and_exports(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    async def run():
        app = AIVScriptApp(offline=True)
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.click("#demo")
            for _ in range(40):
                await pilot.pause(0.1)
                if app.script:
                    break
            assert app.script is not None
            assert app.query_one("#shots").row_count > 0
            assert app.current_shot_id
            app._export_all()
            assert (tmp_path / "output").exists()

    asyncio.run(run())
