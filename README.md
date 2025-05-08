# Princeton Eats

Welcome to Princeton Eats.

Run the `setup.sh` script which will set up a virtual environment with the necessary requirements, and save a random `APP_SECRET_KEY` for CAS authentication. Then, refer to Yusuf's email to find the `DATABASE_URL` and export it as an environment variable with this name.

Then, to run the app on `localhost:8000` run the following:

```bash
python src/princetoneats/app.py
```

To perform unit-tests do the following:

1. Modify `src/princetoneats/app.py` lines 7-9 to read

```
import princetoneats.scrapedining as scrapedining
import princetoneats.auth as auth
import princetoneats.database as database
```

This is required for `pytest` to work. Then, run `pytest` in the terminal to run unit-tests.

**Importantly, you have to change these lines back to their original state in order to run the app.**

--
Created by Yusuf, Adham, Ndongo, Achilles, Akuei
