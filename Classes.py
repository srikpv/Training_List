class Training_Category:
    def __init__(self, id, category):
        self.id = id
        self.category = category
    
class Training_Knowledge_Area:
    def __init__(self, id, knowledge_area):
        self.id = id
        self.knowledge_area = knowledge_area

class Training:
    def __init__(self, id, category, knowledge_area, title, link, description, free, advanced):
        self.id = id
        self.category = category
        self.knowledge_area = knowledge_area
        self.title = title
        self.link = link
        self.description = description
        self.free = free
        self.advanced = advanced

class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

class Training_Assignment:
    def __init__(self, id, training_id, category, knowledge_area, title, link, description, free, advanced, user_id, name, email, approved, approved_by, date_approved, finance_approved, finance_approved_by, finance_date_approved):
        self.id = id
        self.training_id = training_id
        self.category = category
        self.knowledge_area = knowledge_area
        self.title = title
        self.link = link
        self.description = description
        self.free = free
        self.advanced = advanced
        self.user_id = user_id
        self.name = name
        self.email = email
        self.approved = approved
        self.approved_by = approved_by
        self.date_approved = date_approved
        self.finance_approved = finance_approved
        self.finance_approved_by = finance_approved_by
        self.finance_date_approved = finance_date_approved

class Approver:
    def __init__(self, id, name, email, code):
        self.id = id
        self.name = name
        self.email = email
        self.code = code
        
class Finance_Approver:
    def __init__(self, id, name, email, code):
        self.id = id
        self.name = name
        self.email = email
        self.code = code
