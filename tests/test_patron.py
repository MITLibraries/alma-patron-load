import datetime

from bs4 import BeautifulSoup
from freezegun import freeze_time

from patronload.patron import (
    format_phone_number,
    patron_xml_from_records,
    populate_common_fields,
    populate_staff_fields,
    populate_student_fields,
)

SIX_MONTHS = "2023-09-01Z"
TWO_YEARS = "2025-09-01Z"


def test_format_phone_number_valid_value_succeeds():
    assert format_phone_number("1111111111") == "111-111-1111"


def test_format_phone_number_invalid_value_is_returned():
    assert format_phone_number("abcd") == "abcd"


@freeze_time("2023-03-01")
def test_patron_xml_from_records_staff_success(caplog):
    with open(
        "tests/fixtures/staff_patron_xml_record_all_values.xml", "r", encoding="utf8"
    ) as xml_file_all_values, open(
        "tests/fixtures/staff_patron_xml_record_krb_and_null_values.xml",
        "r",
        encoding="utf8",
    ) as xml_file_krb_and_null_values:
        staff_database_record_with_null_values = (
            "222222222",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        staff_database_record_with_all_values = (
            "444444444",
            "STAFF_KRB_NAME@MIT.EDU",
            "STAFF_KRB_NAME",
            "44444444444444",
            "Doe, Jane",
            "AA-B1-11",
            "5555555555",
            datetime.datetime(2023, 6, 30, 0, 0),
            "27",
            "Staff - Lincoln Labs",
            "10000948",
            "LL-Homeland Protection & Air Traffic Con",
            "Part-time Flexible/LL",
            "Part-time Flexible/LL",
        )
        staff_database_record_krb_and_null_values = (
            "666666666",
            None,
            "STAFF_KRB_NAME",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        expected_staff_xml_output_from_all_values = BeautifulSoup(
            xml_file_all_values.read(),
            features="xml",
        )
        expected_staff_xml_output_krb_and_null_values = BeautifulSoup(
            xml_file_krb_and_null_values.read(),
            features="xml",
        )
        results = patron_xml_from_records(
            "staff",
            [
                staff_database_record_with_null_values,
                staff_database_record_with_all_values,
                staff_database_record_krb_and_null_values,
            ],
        )
        assert next(results) == expected_staff_xml_output_from_all_values
        assert (
            "Rejected record: MIT ID # '222222222', missing field KRB_NAME_UPPERCASE"
        ) in caplog.text
        assert (
            next(results).prettify()
            == expected_staff_xml_output_krb_and_null_values.prettify()
        )


@freeze_time("2023-03-01")
def test_patron_xml_from_records_student_success(caplog):
    with open(
        "tests/fixtures/student_patron_xml_record_all_values.xml", "r", encoding="utf8"
    ) as xml_file_all_values, open(
        "tests/fixtures/student_patron_xml_record_krb_and_null_values.xml",
        "r",
        encoding="utf8",
    ) as xml_file_krb_and_null_values:
        student_database_record_with_null_values = (
            "111111111",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        student_database_record_with_all_values = (
            "333333333",
            "STUDENT_KRB_NAME@MIT.EDU",
            "STUDENT_KRB_NAME",
            "33333333333333",
            "Doe",
            "Jane",
            "Janeth",
            "100 Smith St",
            "Apt 34",
            "Cambridge",
            "MA",
            "00000",
            "5555555555",
            "4444444444",
            "3333333333",
            "G",
            "1",
        )
        student_database_record_krb_and_null_values = (
            "555555555",
            None,
            "STUDENT_KRB_NAME",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        expected_student_xml_output_from_all_values = BeautifulSoup(
            xml_file_all_values.read(),
            features="xml",
        )
        expected_student_xml_output_krb_and_null_values = BeautifulSoup(
            xml_file_krb_and_null_values.read(),
            features="xml",
        )
        results = patron_xml_from_records(
            "student",
            [
                student_database_record_with_null_values,
                student_database_record_with_all_values,
                student_database_record_krb_and_null_values,
            ],
        )
        assert next(results) == expected_student_xml_output_from_all_values
        assert (
            "Rejected record: MIT ID # '111111111', missing field KRB_NAME_UPPERCASE"
            in caplog.text
        )
        assert (
            next(results).prettify()
            == expected_student_xml_output_krb_and_null_values.prettify()
        )


def test_populate_common_fields_staff_all_values_success(
    staff_patron_template, staff_patron_all_values_dict
):
    patron_xml_record = populate_common_fields(
        staff_patron_template,
        staff_patron_all_values_dict,
        SIX_MONTHS,
        TWO_YEARS,
    )
    assert patron_xml_record.primary_id.string == "STAFF_KRB_NAME@MIT.EDU"
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert (
        patron_xml_record.emails.email.email_address.string == "STAFF_KRB_NAME@MIT.EDU"
    )
    assert patron_xml_record.find_all("user_identifier")[0].value.string == "222222222"
    assert (
        patron_xml_record.find_all("user_identifier")[1].value.string
        == "22222222222222"
    )


def test_populate_common_fields_staff_null_values_success(
    staff_patron_template,
):
    staff_patron_null_values_dict = {
        "FULL_NAME": None,
        "OFFICE_ADDRESS": None,
        "OFFICE_PHONE": None,
        "MIT_ID": "222222222",
        "EMAIL_ADDRESS": None,
        "APPOINTMENT_END_DATE": None,
        "KRB_NAME_UPPERCASE": "STAFF_KRB_NAME",
        "LIBRARY_PERSON_TYPE_CODE": None,
        "LIBRARY_PERSON_TYPE": None,
        "ORG_UNIT_ID": None,
        "ORG_UNIT_TITLE": None,
        "POSITION_TITLE": None,
        "DIRECTORY_TITLE": None,
        "LIBRARY_ID": None,
    }
    patron_xml_record = populate_common_fields(
        staff_patron_template,
        staff_patron_null_values_dict,
        SIX_MONTHS,
        TWO_YEARS,
    )
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert (
        patron_xml_record.user_identifiers.user_identifier.value.string == "222222222"
    )
    assert not list(patron_xml_record.emails.children)
    assert len(list(patron_xml_record.find_all("user_identifier"))) == 1


def test_populate_common_fields_student_all_values_success(
    student_patron_template, student_patron_all_values_dict
):
    patron_xml_record = populate_common_fields(
        student_patron_template,
        student_patron_all_values_dict,
        SIX_MONTHS,
        TWO_YEARS,
    )
    assert patron_xml_record.primary_id.string == "STUDENT_KRB_NAME@MIT.EDU"
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert (
        patron_xml_record.emails.email.email_address.string
        == "STUDENT_KRB_NAME@MIT.EDU"
    )
    assert patron_xml_record.find_all("user_identifier")[0].value.string == "111111111"
    assert (
        patron_xml_record.find_all("user_identifier")[1].value.string
        == "11111111111111"
    )


def test_populate_common_fields_student_null_values_success(
    student_patron_template,
):
    student_patron_null_values_dict = {
        "EMAIL_ADDRESS": None,
        "FIRST_NAME": None,
        "HOME_DEPARTMENT": None,
        "KRB_NAME_UPPERCASE": "STUDENT_KRB_NAME",
        "LAST_NAME": None,
        "LIBRARY_ID": None,
        "MIDDLE_NAME": None,
        "MIT_ID": "111111111",
        "OFFICE_PHONE": None,
        "STUDENT_YEAR": None,
        "TERM_CITY": None,
        "TERM_PHONE1": None,
        "TERM_PHONE2": None,
        "TERM_STATE": None,
        "TERM_STREET1": None,
        "TERM_STREET2": None,
        "TERM_ZIP": None,
    }
    patron_xml_record = populate_common_fields(
        student_patron_template,
        student_patron_null_values_dict,
        SIX_MONTHS,
        TWO_YEARS,
    )
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert (
        patron_xml_record.user_identifiers.user_identifier.value.string == "111111111"
    )
    assert not list(patron_xml_record.emails.children)
    assert len(list(patron_xml_record.find_all("user_identifier"))) == 1


def test_populate_staff_fields_all_values_success(
    staff_patron_template, staff_patron_all_values_dict
):
    patron_xml_record = populate_staff_fields(
        staff_patron_template,
        staff_patron_all_values_dict,
    )
    assert patron_xml_record.last_name.string == "Doe"
    assert patron_xml_record.first_name.string == "Jane"
    assert patron_xml_record.user_group.string == "27"
    assert patron_xml_record.user_group["desc"] == "Staff - Lincoln Labs"
    assert patron_xml_record.line1.string == "AA-B1-11"
    assert patron_xml_record.phone_number.string == "555-555-5555"
    assert patron_xml_record.statistic_category.string == "NK"
    assert (
        patron_xml_record.statistic_category["desc"]
        == "LL-Homeland Protection & Air Traffic Con"
    )


def test_populate_staff_fields_null_values_success(
    staff_patron_template, staff_patron_all_values_dict
):
    for key in [k for k in staff_patron_all_values_dict.keys() if k != "MIT_ID"]:
        staff_patron_all_values_dict[key] = None
    patron_xml_record = populate_staff_fields(
        staff_patron_template,
        staff_patron_all_values_dict,
    )
    assert patron_xml_record.last_name.string is None
    assert patron_xml_record.first_name.string is None
    assert patron_xml_record.user_group.string == ""
    assert patron_xml_record.user_group["desc"] == ""
    assert patron_xml_record.line1.string == "NO ADDRESS ON FILE IN DATA WAREHOUSE"
    assert patron_xml_record.phones.is_empty_element
    assert patron_xml_record.statistic_category.string == "ZQ"
    assert patron_xml_record.statistic_category["desc"] == "Unknown"


def test_populate_student_fields_all_values_success(
    student_patron_template, student_patron_all_values_dict
):
    patron_xml_record = populate_student_fields(
        student_patron_template,
        student_patron_all_values_dict,
    )
    assert patron_xml_record.first_name.string == "Jane"
    assert patron_xml_record.middle_name.string == "Janeth"
    assert patron_xml_record.last_name.string == "Doe"
    assert patron_xml_record.address.line1.string == "100 Smith St"
    assert patron_xml_record.line3.string == "Apt 34"
    assert patron_xml_record.city.string == "Cambridge"
    assert patron_xml_record.state_province.string == "MA"
    assert patron_xml_record.postal_code.string == "00000"
    assert patron_xml_record.find_all("phone_number")[0].string == "333-333-3333"
    assert patron_xml_record.find_all("phone_number")[1].string == "555-555-5555"
    assert patron_xml_record.statistic_category.string == "SN"
    assert patron_xml_record.user_group.string == "32"


def test_populate_student_fields_null_values_success(
    student_patron_template, student_patron_all_values_dict
):
    for key in [k for k in student_patron_all_values_dict.keys() if k != "MIT_ID"]:
        student_patron_all_values_dict[key] = None
    patron_xml_record = populate_student_fields(
        student_patron_template,
        student_patron_all_values_dict,
    )
    assert patron_xml_record.first_name.string == ""
    assert patron_xml_record.middle_name.string == ""
    assert patron_xml_record.last_name.string == ""
    assert (
        patron_xml_record.address.line1.string == "NO ADDRESS ON FILE IN DATA WAREHOUSE"
    )
    assert patron_xml_record.line3.string == ""
    assert patron_xml_record.city.string == ""
    assert patron_xml_record.state_province.string == ""
    assert patron_xml_record.postal_code.string == ""
    assert patron_xml_record.phones.is_empty_element
    assert patron_xml_record.statistic_category.string == "ZZ"
    assert patron_xml_record.user_group.string is None


def test_populate_student_fields_no_office_phone_success(
    student_patron_template, student_patron_all_values_dict
):
    student_patron_all_values_dict["OFFICE_PHONE"] = None
    patron_xml_record = populate_student_fields(
        student_patron_template,
        student_patron_all_values_dict,
    )
    assert patron_xml_record.phone_number.string == "555-555-5555"
    assert len(list(patron_xml_record.find_all("phone_number"))) == 1


def test_populate_student_fields_no_office_phone_no_term_phone1_success(
    student_patron_template, student_patron_all_values_dict
):
    student_patron_all_values_dict["OFFICE_PHONE"] = None
    student_patron_all_values_dict["TERM_PHONE1"] = None
    patron_xml_record = populate_student_fields(
        student_patron_template,
        student_patron_all_values_dict,
    )
    assert patron_xml_record.phone_number.string == "444-444-4444"
    assert len(list(patron_xml_record.find_all("phone_number"))) == 1


def test_populate_student_fields_undergraduate_user_group_success(
    student_patron_template, student_patron_all_values_dict
):
    student_patron_all_values_dict["STUDENT_YEAR"] = "1"
    patron_xml_record = populate_student_fields(
        student_patron_template,
        student_patron_all_values_dict,
    )
    assert patron_xml_record.user_group.string == "31"


def test_populate_student_fields_non_mit_user_group_success(
    student_patron_template, student_patron_all_values_dict
):
    student_patron_all_values_dict["HOME_DEPARTMENT"] = "NIV"
    patron_xml_record = populate_student_fields(
        student_patron_template,
        student_patron_all_values_dict,
    )
    assert patron_xml_record.user_group.string == "54"
